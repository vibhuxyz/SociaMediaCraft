import logging
from fastapi import FastAPI , APIRouter
from pydantic import BaseModel
from config.settings import settings
from providers.llm.universal_provider import UniversalLLMProvider
from workflow.graph import build_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-engine")



logger.info("Init V3 LLM Provider")

llm_provider = UniversalLLMProvider(
    openai_key=settings.OPENAI_API_KEY,
    anthropic_key=settings.ANTHROPIC_API_KEY
)

planning_graph = build_graph()



app = FastAPI(
    title="VideoCraft v3",
    description="The Pure Intelligence Layer",
    version="3.1.0"
)

v1_router = APIRouter(prefix="/api/v1", tags=["V1 Pipeline"])


class GeneratePlanRequest(BaseModel):
    prompt: str
    thread_id: str = "default"


@v1_router.post("/generate-plan")
async def v1_generate_plan(request: GeneratePlanRequest):
    config = {"configurable": {"thread_id": request.thread_id}}
    final_state = await planning_graph.ainvoke({"prompt": request.prompt}, config)
    return final_state["production_plan"]

app.include_router(v1_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
