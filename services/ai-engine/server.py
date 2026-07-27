import logging
from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

from config.settings import settings
from providers.llm.universal_provider import UniversalLLMProvider
from workflow.graph import build_graph

# Fix #1 & #2: Generation pipeline + Project Context Store
from generation.pipeline import run_image_pipeline, run_video_pipeline, run_audio_pipeline
from generation.context_store import store_context, context_exists
from generation.scheduler import ProviderExhaustedError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-engine")

logger.info("Init V3 LLM Provider")

llm_provider = UniversalLLMProvider(
    openai_key=settings.OPENAI_API_KEY,
    anthropic_key=settings.ANTHROPIC_API_KEY,
    openrouter_key=settings.OPENROUTER_API_KEY,
    custom_key=settings.CUSTOM_API_KEY,
    custom_base=settings.CUSTOM_API_BASE
)

planning_graph = build_graph(interrupt_after_clarification=True)

app = FastAPI(
    title="VideoCraft AI Engine",
    description="The Pure Intelligence Layer — owns all AI logic: planning, prompt building, and provider dispatch",
    version="4.0.0"
)

v1_router = APIRouter(prefix="/api/v1", tags=["V1 Pipeline"])


# ---------------------------------------------------------------------------
# Planning endpoint (unchanged)
# ---------------------------------------------------------------------------

class GeneratePlanRequest(BaseModel):
    prompt: str
    template_name: str = "Advertisement"
    thread_id: str
    clarification_answers: Optional[dict[str, str]] = None


@v1_router.post("/generate-plan")
async def v1_generate_plan(request: GeneratePlanRequest):
    config = {"configurable": {"thread_id": request.thread_id}}

    state_snapshot = planning_graph.get_state(config)

    if state_snapshot.next and request.clarification_answers is not None:
        logger.info(f"[thread={request.thread_id}] Resuming with clarification answers")
        planning_graph.update_state(config, {"clarification_answers": request.clarification_answers})
        final_state = await planning_graph.ainvoke(None, config)
    else:
        initial_state = {"prompt": request.prompt, "template_name": request.template_name}
        final_state = await planning_graph.ainvoke(initial_state, config)

        current_state = planning_graph.get_state(config)
        if current_state.next and not final_state.get("clarification_questions"):
            logger.info(f"[thread={request.thread_id}] No clarification needed, auto-resuming")
            final_state = await planning_graph.ainvoke(None, config)

    if final_state.get("clarification_questions") and not final_state.get("production_plan"):
        return {"clarification_questions": final_state["clarification_questions"]}

    return final_state.get("production_plan", {"status": "No plan generated"})


# ---------------------------------------------------------------------------
# Fix #2 — Project Context Store endpoint
# Called once per job by the Worker after it receives the finished plan.
# Stores character sheets, environment sheets, brand guide, and art direction
# in Redis so every shot can reference them without repeating the data.
# ---------------------------------------------------------------------------

class StoreContextRequest(BaseModel):
    job_id: str
    context: Dict[str, Any]
    ttl_seconds: int = 86400


@v1_router.post("/store-context")
async def v1_store_context(request: StoreContextRequest):
    """Persist the ProjectContext for a job in Redis.

    The orchestrator / worker calls this once after the production plan is
    ready.  Every subsequent generation job for that parent job_id can then
    resolve characters, environments, brand, and art-direction from Redis
    instead of embedding them in every queue message.
    """
    await store_context(request.job_id, request.context, request.ttl_seconds)
    return {"status": "ok", "job_id": request.job_id}


@v1_router.get("/context-status/{job_id}")
async def v1_context_status(job_id: str):
    """Verify that the ProjectContext for *job_id* is present in Redis.

    Called by the orchestrator's invariant gate immediately after
    POST /store-context.  Returns { exists, key } so the caller can
    confirm the write succeeded before dispatching any generation jobs.

    If exists=false, the orchestrator must NOT dispatch jobs — it should
    abort and surface an error so the missing-context failure is caught
    at the orchestrator level, not per-worker-job.

    Debug tip:
        redis-cli GET job:<job_id>:project_context
    """
    key    = f"job:{job_id}:project_context"
    exists = await context_exists(job_id)
    logger.info(f"[Server] context-status job={job_id!r}  exists={exists}  key={key!r}")
    return {"exists": exists, "key": key, "job_id": job_id}


# ---------------------------------------------------------------------------
# Fix #1 — Generation endpoint: AI Engine owns prompt building
#
# The Worker sends a *thin* job descriptor (base_prompt + references).
# The AI Engine resolves the full prompt from the stored ProjectContext,
# then calls the appropriate provider adapter (Flux / Veo / ElevenLabs / …).
#
# Switching Flux → GPT Image → Imagen only requires changing the adapter —
# the Worker and the queue message format stay untouched.
# ---------------------------------------------------------------------------

@app.post("/generate/{queue_name}")
async def generate_asset(queue_name: str, payload: Dict[str, Any]):
    logger.info(f"[REST API] /generate/{queue_name} — job={payload.get('job_id')}")

    # Save payload for inspection (kept from original behaviour)
    import json
    job_id = payload.get('job_id', 'unknown')
    with open(f"worker_payload_{job_id}.json", "w") as f:
        json.dump(payload, f, indent=2)

    try:
        if queue_name == "image-generation":
            return await run_image_pipeline(payload)
        elif queue_name == "video-generation":
            return await run_video_pipeline(payload)
        elif queue_name in ("voice-generation", "music-generation", "sfx-generation"):
            audio_type = queue_name.split("-")[0]   # "voice" | "music" | "sfx"
            return await run_audio_pipeline(payload, audio_type=audio_type)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown queue: {queue_name}")
    except ProviderExhaustedError as exc:
        # All providers failed for this job — return 503 so the worker nacks
        # the RabbitMQ message and it can be retried or dead-lettered.
        logger.error(f"[REST API] All providers exhausted: {exc}")
        raise HTTPException(status_code=503, detail=str(exc))
    except RuntimeError as exc:
        # Typically means the ProjectContext hasn't been stored yet
        logger.error(f"[REST API] Pipeline error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


app.include_router(v1_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
