"""
Prompt Builder  (Fix #1)
========================
The AI Engine — not the Worker — owns prompt construction.

The worker sends a *thin* job descriptor:
  {
    "job_id": "img_S1_1",
    "job_id_parent": "proj-xxx",   # used to look up the ProjectContext
    "type": "image",
    "references": {
      "character_id": "char_001",
      "environment_id": "env_001"
    },
    "base_prompt": "Barista prepares espresso with care",   # raw scene intent
    "negative_prompt": "...",
    "generation": { "seed": 1001, "cfg": 7.5, "shot_type": "medium", ... }
  }

Pipeline (all steps inside this module and prompt_optimizer.py):
  1. Load ProjectContext from Redis          (context_store)
  2. Resolve character / environment / brand / art direction
  3. Assemble raw prompt string              (_build_image_prompt)
  4. Run Prompt Optimizer                    (prompt_optimizer)
     ├── Deduplication
     ├── Character enrichment
     ├── Environment enrichment
     ├── Action enrichment
     ├── Camera enrichment
     ├── Lighting enrichment
     ├── Style preset injection
     ├── Composition enrichment
     ├── Emotional intent
     └── Provider-specific negative prompt
  5. Return enriched payload to the Pipeline / Adapter

Switching providers only requires changing the provider_name passed to the
optimizer — nothing in the Worker changes.
"""

import logging
from typing import Any, Optional

from generation.context_store import (
    load_context,
    resolve_character,
    resolve_environment,
    resolve_brand,
    resolve_art_direction,
)
from generation.prompt_optimizer import optimize_image_prompt, optimize_video_prompt

logger = logging.getLogger("ai-engine.prompt_builder")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _detect_provider(job: dict[str, Any]) -> str:
    """Extract a normalised provider name for the negative-prompt library lookup."""
    provider = job.get("provider", {})
    if isinstance(provider, dict):
        return (provider.get("name") or provider.get("model") or "flux").lower()
    return str(provider).lower() or "flux"


# ---------------------------------------------------------------------------
# Public entry points — one per asset type
# ---------------------------------------------------------------------------

async def build_image_prompt(job: dict[str, Any]) -> dict[str, Any]:
    """Resolve context, assemble, optimize, and return the enriched image payload."""
    ctx = await load_context(job["job_id_parent"])

    char  = resolve_character(ctx,   job.get("references", {}).get("character_id", ""))
    env   = resolve_environment(ctx, job.get("references", {}).get("environment_id", ""))
    brand = resolve_brand(ctx)
    art   = resolve_art_direction(ctx)

    # Also pull emotion and strategy hints from context if present
    emotion = ctx.get("emotion") or {}

    # Step 1-3: raw assembly
    raw_prompt = _build_raw_image_prompt(
        base=job.get("base_prompt", ""),
        character=char,
        environment=env,
        brand=brand,
        art=art,
    )

    # Step 4: optimization pipeline
    provider_name = _detect_provider(job)
    resolved = {
        "character":    char,
        "environment":  env,
        "brand":        brand,
        "art_direction": art,
        "emotion":      emotion,
    }
    optimized_prompt, negative_prompt = optimize_image_prompt(
        raw_prompt=raw_prompt,
        resolved=resolved,
        generation=job.get("generation"),
        provider_name=provider_name,
        existing_negative=job.get("negative_prompt", ""),
    )

    logger.info(
        f"[PromptBuilder] image  job={job['job_id']}  "
        f"raw={len(raw_prompt)}c → optimized={len(optimized_prompt)}c  "
        f"provider={provider_name!r}"
    )

    return {
        "job_id":          job["job_id"],
        "provider":        job.get("provider", {}),
        "prompt":          optimized_prompt,
        "negative_prompt": negative_prompt,
        "generation":      job.get("generation", {}),
        "input_image_urls": job.get("input_image_urls", []),
        # Resolved pieces available to adapters / debug logs
        "_resolved": resolved,
        "_raw_prompt": raw_prompt,
    }


async def build_video_prompt(job: dict[str, Any]) -> dict[str, Any]:
    """Resolve context, assemble, optimize, and return the enriched video payload."""
    ctx = await load_context(job["job_id_parent"])

    char  = resolve_character(ctx,   job.get("references", {}).get("character_id", ""))
    env   = resolve_environment(ctx, job.get("references", {}).get("environment_id", ""))
    brand = resolve_brand(ctx)
    art   = resolve_art_direction(ctx)
    emotion = ctx.get("emotion") or {}

    raw_prompt = _build_raw_video_prompt(
        base=job.get("base_prompt", ""),
        character=char,
        environment=env,
        brand=brand,
        art=art,
        camera_motion=job.get("generation", {}).get("camera_motion", "Static"),
    )

    provider_name = _detect_provider(job)
    resolved = {
        "character":    char,
        "environment":  env,
        "brand":        brand,
        "art_direction": art,
        "emotion":      emotion,
    }
    optimized_prompt, negative_prompt = optimize_video_prompt(
        raw_prompt=raw_prompt,
        resolved=resolved,
        generation=job.get("generation"),
        provider_name=provider_name,
        existing_negative=job.get("negative_prompt", ""),
    )

    logger.info(
        f"[PromptBuilder] video  job={job['job_id']}  "
        f"raw={len(raw_prompt)}c → optimized={len(optimized_prompt)}c  "
        f"provider={provider_name!r}"
    )

    return {
        "job_id":          job["job_id"],
        "provider":        job.get("provider", {}),
        "prompt":          optimized_prompt,
        "negative_prompt": negative_prompt,
        "generation":      job.get("generation", {}),
        "input_image_urls": job.get("input_image_urls", []),
        "_resolved": resolved,
        "_raw_prompt": raw_prompt,
    }


# ---------------------------------------------------------------------------
# Raw prompt assembly  (pre-optimizer)
# Kept intentionally simple — the optimizer handles enrichment.
# Swap these functions when you change output format requirements.
# ---------------------------------------------------------------------------

def _build_raw_image_prompt(
    base: str,
    character: Optional[dict],
    environment: Optional[dict],
    brand: Optional[dict],
    art: Optional[dict],
) -> str:
    """Assemble a raw multi-clause prompt from resolved context pieces.

    This is deliberately minimal — the PromptOptimizer handles all enrichment.
    """
    parts: list[str] = [base]

    if character:
        appearance = character.get("appearance", {})
        outfit = ""
        if character.get("outfits"):
            first = character["outfits"][0]
            outfit = first if isinstance(first, str) else first.get("description", "")
        parts.append(
            f"Character: {character.get('name', '')} — "
            f"{appearance.get('hair', '')} hair, "
            f"{appearance.get('skin', '')} skin"
            + (f", wearing {outfit}" if outfit else "")
        )

    if environment:
        parts.append(
            f"Setting: {environment.get('name', '')} — "
            f"{environment.get('architecture', '')}, "
            f"{environment.get('lighting', '')} lighting"
        )

    if art:
        parts.append(
            f"Style: {art.get('visual_style', 'Cinematic')}, "
            f"{art.get('color_grading', 'Natural')} grade"
        )

    if brand and brand.get("personality"):
        parts.append(f"Brand feel: {brand['personality']}")

    return ". ".join(filter(None, parts))


def _build_raw_video_prompt(
    base: str,
    character: Optional[dict],
    environment: Optional[dict],
    brand: Optional[dict],
    art: Optional[dict],
    camera_motion: str = "Static",
) -> str:
    image_part = _build_raw_image_prompt(base, character, environment, brand, art)
    return f"{image_part}. Camera motion: {camera_motion}"
