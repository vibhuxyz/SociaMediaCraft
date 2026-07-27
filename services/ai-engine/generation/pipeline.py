"""
Generation Pipeline  (Fix #1 — AI Engine owns AI logic)
=========================================================
Entry-point that wires:
  1. Prompt building    (generation/prompt_builder.py)
  2. Generation Scheduler  →  Provider Router  →  Adapter

Worker  →  thin descriptor  →  AI Engine
                                  │
                             prompt_builder
                                  │
                               scheduler  ←── reads strategy / preferred_provider
                                  │
                            provider_router  ←── picks Flux Schnell / GPT Image / Veo / …
                                  │
                               adapter  ←── actual API call
"""

import logging
from typing import Any

from generation.prompt_builder import build_image_prompt, build_video_prompt
from generation.scheduler import schedule_generation

logger = logging.getLogger("ai-engine.pipeline")


async def run_image_pipeline(job: dict[str, Any]) -> dict[str, Any]:
    """Full image pipeline: resolve context → build prompt → schedule → provider."""
    logger.info(f"[Pipeline] IMAGE  job={job.get('job_id')}")

    enriched = await build_image_prompt(job)
    logger.info(f"[Pipeline] Prompt built ({len(enriched['prompt'])} chars) → scheduling")

    return await schedule_generation("image", enriched)


async def run_video_pipeline(job: dict[str, Any]) -> dict[str, Any]:
    """Full video pipeline: resolve context → build prompt → schedule → provider."""
    logger.info(f"[Pipeline] VIDEO  job={job.get('job_id')}")

    enriched = await build_video_prompt(job)
    logger.info(f"[Pipeline] Prompt built ({len(enriched['prompt'])} chars) → scheduling")

    return await schedule_generation("video", enriched)


async def run_audio_pipeline(job: dict[str, Any], audio_type: str) -> dict[str, Any]:
    """Audio pipeline — no prompt building needed (text is already literal)."""
    logger.info(f"[Pipeline] AUDIO({audio_type})  job={job.get('job_id')}")
    return await schedule_generation(audio_type, job)  # type: ignore[arg-type]
