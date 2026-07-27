"""
Provider Router
===============
Selects and dispatches to the right generation provider based on a
strategy hint (`fast` | `quality` | `cheap` | `auto`) and the asset type.

Provider Registry
-----------------
Each provider entry declares:
  - name          Human-readable label
  - adapter_fn    Async callable that takes an enriched payload and returns
                  { status, asset_url }  (same contract as all adapters)
  - asset_types   Which asset types this provider supports
  - strategies    Which strategies it's eligible for
  - cost_tier     "low" | "medium" | "high" — used when strategy="cheap"
  - quality_tier  "standard" | "high" | "ultra" — used when strategy="quality"

Adding a new provider = add one entry to PROVIDER_REGISTRY.
Nothing in the Worker or Orchestrator changes.
"""

import logging
from typing import Any, Callable, Awaitable, Literal

logger = logging.getLogger("ai-engine.provider_router")

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

Strategy   = Literal["fast", "quality", "cheap", "auto"]
AssetType  = Literal["image", "video", "voice", "music", "sfx"]
AdapterFn  = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


# ---------------------------------------------------------------------------
# Provider Registry
# ---------------------------------------------------------------------------

def _image_adapter() -> AdapterFn:
    from adapters.image import generate_image
    return generate_image

def _video_adapter() -> AdapterFn:
    from adapters.video import generate_video
    return generate_video

def _audio_adapter(audio_type: str) -> AdapterFn:
    from adapters import generate_audio
    async def _fn(payload: dict) -> dict:
        return await generate_audio(payload, audio_type=audio_type)
    return _fn


# Registry: ordered by preference within each strategy tier.
# The router picks the first matching entry.
PROVIDER_REGISTRY: list[dict[str, Any]] = [
    # ── Image providers ──────────────────────────────────────────────────
    {
        "name": "Flux Schnell",
        "asset_types": ["image"],
        "strategies": ["fast", "auto"],
        "cost_tier": "low",
        "quality_tier": "standard",
        "adapter_fn": _image_adapter,
    },
    {
        "name": "Flux Pro",
        "asset_types": ["image"],
        "strategies": ["quality", "auto"],
        "cost_tier": "medium",
        "quality_tier": "high",
        "adapter_fn": _image_adapter,
    },
    {
        "name": "GPT Image",
        "asset_types": ["image"],
        "strategies": ["quality"],
        "cost_tier": "high",
        "quality_tier": "ultra",
        "adapter_fn": _image_adapter,
    },
    {
        "name": "Imagen",
        "asset_types": ["image"],
        "strategies": ["quality"],
        "cost_tier": "high",
        "quality_tier": "ultra",
        "adapter_fn": _image_adapter,
    },
    {
        "name": "SDXL",
        "asset_types": ["image"],
        "strategies": ["cheap", "auto"],
        "cost_tier": "low",
        "quality_tier": "standard",
        "adapter_fn": _image_adapter,
    },
    # ── Video providers ──────────────────────────────────────────────────
    {
        "name": "Veo 3",
        "asset_types": ["video"],
        "strategies": ["quality", "auto"],
        "cost_tier": "high",
        "quality_tier": "ultra",
        "adapter_fn": _video_adapter,
    },
    {
        "name": "Runway Gen-4",
        "asset_types": ["video"],
        "strategies": ["fast", "auto"],
        "cost_tier": "medium",
        "quality_tier": "high",
        "adapter_fn": _video_adapter,
    },
    {
        "name": "Kling",
        "asset_types": ["video"],
        "strategies": ["cheap"],
        "cost_tier": "low",
        "quality_tier": "standard",
        "adapter_fn": _video_adapter,
    },
    # ── Audio providers ──────────────────────────────────────────────────
    {
        "name": "ElevenLabs",
        "asset_types": ["voice"],
        "strategies": ["fast", "quality", "auto"],
        "cost_tier": "medium",
        "quality_tier": "high",
        "adapter_fn": lambda: _audio_adapter("voice"),
    },
    {
        "name": "Suno",
        "asset_types": ["music"],
        "strategies": ["fast", "quality", "auto", "cheap"],
        "cost_tier": "low",
        "quality_tier": "high",
        "adapter_fn": lambda: _audio_adapter("music"),
    },
    {
        "name": "ElevenLabs SFX",
        "asset_types": ["sfx"],
        "strategies": ["fast", "quality", "auto", "cheap"],
        "cost_tier": "low",
        "quality_tier": "high",
        "adapter_fn": lambda: _audio_adapter("sfx"),
    },
]


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

def select_provider(
    asset_type: AssetType,
    strategy: Strategy = "auto",
    preferred_name: str | None = None,
) -> dict[str, Any]:
    """Return the best matching provider entry for the given asset type and strategy.

    Selection priority:
      1. If `preferred_name` is specified and available, use it directly.
      2. Otherwise, pick the first registry entry that matches both
         `asset_type` and `strategy`.

    Raises ValueError if no provider is found.
    """
    candidates = [
        p for p in PROVIDER_REGISTRY
        if asset_type in p["asset_types"]
    ]

    if not candidates:
        raise ValueError(f"[ProviderRouter] No providers registered for asset_type={asset_type!r}")

    # Honour explicit provider preference (e.g. from the job descriptor)
    if preferred_name:
        for p in candidates:
            if p["name"].lower() == preferred_name.lower():
                logger.info(f"[ProviderRouter] Explicit provider={preferred_name!r} selected for {asset_type}/{strategy}")
                return p
        logger.warning(
            f"[ProviderRouter] Preferred provider {preferred_name!r} not found; "
            f"falling back to strategy={strategy!r}"
        )

    # Strategy-based selection
    strategy_candidates = [p for p in candidates if strategy in p["strategies"]]
    if not strategy_candidates:
        # Fallback: any provider for this asset type
        strategy_candidates = candidates
        logger.warning(
            f"[ProviderRouter] No provider for asset_type={asset_type!r} strategy={strategy!r}; "
            f"using first available"
        )

    chosen = strategy_candidates[0]
    logger.info(
        f"[ProviderRouter] Selected provider={chosen['name']!r}"
        f"  asset_type={asset_type}  strategy={strategy}"
        f"  cost={chosen['cost_tier']}  quality={chosen['quality_tier']}"
    )
    return chosen


async def dispatch_to_provider(
    provider_entry: dict[str, Any],
    enriched_payload: dict[str, Any],
) -> dict[str, Any]:
    """Call the provider's adapter function with the enriched payload."""
    adapter_fn: AdapterFn = provider_entry["adapter_fn"]()
    logger.info(
        f"[ProviderRouter] Dispatching job={enriched_payload.get('job_id')!r}"
        f" to provider={provider_entry['name']!r}"
    )
    return await adapter_fn(enriched_payload)
