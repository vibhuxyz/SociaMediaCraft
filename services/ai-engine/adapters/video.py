import asyncio
import logging

logger = logging.getLogger("ai-engine.adapters.video")

# TODO: swap for the real generated asset URL once a real video provider (Veo,
# Runway, Pika, Kling, etc.) is wired in. These are real, publicly viewable
# sample clips so the frontend has something to actually play instead of a
# dead mock-bucket URL.
_SAMPLE_VIDEOS = [
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4",
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4",
]

async def generate_video(payload: dict) -> dict:
    job_id   = payload.get("job_id", "unknown")
    provider = payload.get("_selected_provider") or (payload.get("provider") or {}).get("name", "Veo")
    prompt   = payload.get("prompt", "")
    negative = payload.get("negative_prompt", "")

    logger.info("=" * 60)
    logger.info(f"🎬  VIDEO GENERATION  job={job_id}  provider={provider!r}")
    logger.info(f"Prompt ({len(prompt)} chars):")
    logger.info(f"  {prompt}")
    logger.info(f"Negative ({len(negative)} chars):")
    logger.info(f"  {negative[:200]}{'…' if len(negative) > 200 else ''}")
    logger.info(f"Generation spec: {payload.get('generation', {})}")
    logger.info("=" * 60)

    # Here you would route to Google Veo, Runway, Pika, Kling, etc.
    await asyncio.sleep(4)  # Simulate generation latency

    job_id = payload.get("job_id", "unknown")
    # sum(bytes) instead of hash() so the pick is stable across process restarts
    # (Python's built-in hash() is randomized per-run for strings).
    asset_url = _SAMPLE_VIDEOS[sum(job_id.encode()) % len(_SAMPLE_VIDEOS)]

    return {
        "status": "success",
        "asset_url": asset_url
    }
