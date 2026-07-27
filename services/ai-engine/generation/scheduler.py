"""
Generation Scheduler  (with Retry & Failover)
==============================================
Sits between the pipeline entry-points and the Provider Router.

Responsibilities
----------------
1. Read `strategy` and `preferred_provider` from the enriched job payload.
2. Select an initial provider via the Provider Router.
3. Attempt generation — with exponential-backoff retries on the same provider.
4. On repeated failure, switch to the next eligible provider (failover) and
   restart the retry cycle.
5. Emit structured log entries at every decision point so failures are
   fully traceable without needing a debugger.

Retry & Failover model
-----------------------

  attempt 1  ──► Flux Pro  OK   →  return result
                 (fail)
  attempt 2  ──► Flux Pro  OK   →  return result     ← retry same provider
                 (fail)
  attempt 3  ──► Flux Pro  FAIL → exhausted retries for this provider
                 ↓ failover
  attempt 1  ──► GPT Image OK   →  return result
                 (fail)
  attempt 2  ──► GPT Image FAIL → exhausted retries for this provider
                 ↓ failover
  attempt 1  ──► SDXL      OK   →  return result
                  ...

If all providers are exhausted a ProviderExhaustedError is raised — the
adapter can propagate it to the worker which will nack the RabbitMQ message.

Configuration (per-call overrides via job payload fields)
---------------------------------------------------------
  retry_limit      int   Max retries per provider          (default: MAX_RETRIES_PER_PROVIDER)
  retry_delay_s    float Initial backoff delay in seconds  (default: INITIAL_DELAY_S)
  retry_backoff    float Multiplier applied each retry     (default: BACKOFF_FACTOR)
  retry_max_delay  float Cap on backoff delay              (default: MAX_DELAY_S)
"""

import asyncio
import logging
from typing import Any, Literal

from generation.provider_router import (
    select_provider,
    dispatch_to_provider,
    Strategy,
    PROVIDER_REGISTRY,
    AssetType,
)

logger = logging.getLogger("ai-engine.scheduler")

# ---------------------------------------------------------------------------
# Defaults — all overridable per job via payload fields
# ---------------------------------------------------------------------------

MAX_RETRIES_PER_PROVIDER: int   = 3
INITIAL_DELAY_S:          float = 1.0   # first retry waits 1 s
BACKOFF_FACTOR:           float = 2.0   # doubles each retry: 1s, 2s, 4s
MAX_DELAY_S:              float = 30.0  # never wait longer than 30 s


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------

class ProviderExhaustedError(RuntimeError):
    """All eligible providers failed for this job."""
    def __init__(self, asset_type: str, attempts: list[dict]):
        summary = "; ".join(
            f"{a['provider']} x{a['tries']} ({a['last_error']})"
            for a in attempts
        )
        super().__init__(
            f"[Scheduler] All providers exhausted for asset_type={asset_type!r}. "
            f"Attempt log: {summary}"
        )
        self.attempts = attempts


# ---------------------------------------------------------------------------
# Provider candidate list (for failover)
# ---------------------------------------------------------------------------

def _get_failover_chain(
    asset_type: AssetType,
    strategy: Strategy,
    initial_provider_name: str,
) -> list[dict[str, Any]]:
    """Return the ordered list of providers to try, starting with the initial one.

    The initial provider is always first. The rest are other eligible providers
    for this asset_type + strategy that haven't been tried yet, in registry order.
    """
    candidates = [
        p for p in PROVIDER_REGISTRY
        if asset_type in p["asset_types"] and strategy in p["strategies"]
    ]
    if not candidates:
        # Fall back to all providers for this asset type
        candidates = [p for p in PROVIDER_REGISTRY if asset_type in p["asset_types"]]

    # Put the initially selected provider first, then the rest
    initial = [p for p in candidates if p["name"] == initial_provider_name]
    rest    = [p for p in candidates if p["name"] != initial_provider_name]
    return initial + rest


# ---------------------------------------------------------------------------
# Core retry loop
# ---------------------------------------------------------------------------

async def _try_provider_with_retries(
    provider: dict[str, Any],
    enriched_payload: dict[str, Any],
    retry_limit: int,
    initial_delay: float,
    backoff_factor: float,
    max_delay: float,
) -> dict[str, Any]:
    """Attempt `provider` up to `retry_limit` times with exponential backoff.

    Raises the last exception if all attempts fail.
    """
    delay = initial_delay

    for attempt in range(1, retry_limit + 1):
        try:
            logger.info(
                f"[Scheduler] 🔄 provider={provider['name']!r}"
                f"  attempt={attempt}/{retry_limit}"
                f"  job={enriched_payload.get('job_id')!r}"
            )
            enriched_payload["_selected_provider"] = provider["name"]
            result = await dispatch_to_provider(provider, enriched_payload)

            logger.info(
                f"[Scheduler] ✅ provider={provider['name']!r}"
                f"  attempt={attempt}  job={enriched_payload.get('job_id')!r}"
            )
            return result

        except Exception as exc:
            logger.warning(
                f"[Scheduler] ❌ provider={provider['name']!r}"
                f"  attempt={attempt}/{retry_limit}"
                f"  error={exc!r}"
                f"  job={enriched_payload.get('job_id')!r}"
            )
            if attempt < retry_limit:
                logger.info(f"[Scheduler] ⏳ Retrying in {delay:.1f}s…")
                await asyncio.sleep(delay)
                delay = min(delay * backoff_factor, max_delay)

    # All retries exhausted — re-raise the last exception to trigger failover
    raise exc  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

async def schedule_generation(
    asset_type: AssetType,
    enriched_payload: dict[str, Any],
) -> dict[str, Any]:
    """Select a provider, run with retries, fail over to the next provider if needed.

    Job-level overrides (all optional, read from enriched_payload):
      strategy            fast | quality | cheap | auto   (default: auto)
      preferred_provider  explicit provider name override
      retry_limit         max retries per provider        (default: 3)
      retry_delay_s       initial backoff seconds         (default: 1.0)
      retry_backoff       backoff multiplier              (default: 2.0)
      retry_max_delay     max backoff cap in seconds      (default: 30.0)
    """
    strategy: Strategy = enriched_payload.get("strategy", "auto")  # type: ignore[assignment]
    preferred          = enriched_payload.get("preferred_provider")

    # Validate strategy
    if strategy not in {"fast", "quality", "cheap", "auto"}:
        logger.warning(
            f"[Scheduler] Unknown strategy={strategy!r}"
            f"  job={enriched_payload.get('job_id')}; defaulting to 'auto'"
        )
        strategy = "auto"

    # Per-job retry config
    retry_limit    = int(enriched_payload.get("retry_limit",    MAX_RETRIES_PER_PROVIDER))
    initial_delay  = float(enriched_payload.get("retry_delay_s",  INITIAL_DELAY_S))
    backoff_factor = float(enriched_payload.get("retry_backoff",  BACKOFF_FACTOR))
    max_delay      = float(enriched_payload.get("retry_max_delay", MAX_DELAY_S))

    # Initial provider selection
    initial_provider = select_provider(
        asset_type=asset_type,
        strategy=strategy,
        preferred_name=preferred,
    )

    logger.info(
        f"[Scheduler] Starting  job={enriched_payload.get('job_id')!r}"
        f"  asset_type={asset_type}  strategy={strategy}"
        f"  initial_provider={initial_provider['name']!r}"
        f"  retry_limit={retry_limit}"
    )

    # Build failover chain — initial provider first, then alternates
    failover_chain = _get_failover_chain(asset_type, strategy, initial_provider["name"])

    attempt_log: list[dict] = []

    for provider in failover_chain:
        tries = 0
        last_error = ""
        try:
            result = await _try_provider_with_retries(
                provider=provider,
                enriched_payload=enriched_payload,
                retry_limit=retry_limit,
                initial_delay=initial_delay,
                backoff_factor=backoff_factor,
                max_delay=max_delay,
            )
            # Track which provider actually succeeded
            tries = enriched_payload.get("_retry_count", 1)
            attempt_log.append({"provider": provider["name"], "tries": tries, "last_error": "", "outcome": "success"})
            logger.info(
                f"[Scheduler] 🏁 Succeeded  job={enriched_payload.get('job_id')!r}"
                f"  provider={provider['name']!r}"
            )
            return result

        except Exception as exc:
            last_error = repr(exc)
            tries = retry_limit
            attempt_log.append({"provider": provider["name"], "tries": tries, "last_error": last_error, "outcome": "failed"})
            logger.error(
                f"[Scheduler] 💥 Provider exhausted: {provider['name']!r}"
                f"  after {retry_limit} attempts"
                f"  job={enriched_payload.get('job_id')!r}"
                f"  error={last_error}"
            )
            # Reset delay for next provider's retry cycle
            enriched_payload.pop("_selected_provider", None)

    raise ProviderExhaustedError(asset_type=asset_type, attempts=attempt_log)
