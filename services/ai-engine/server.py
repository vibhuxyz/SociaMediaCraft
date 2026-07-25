import logging
from fastapi import FastAPI , APIRouter
from config.settings import settings
from providers.llm.universal_provider import UniversalLLMProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-engine")



logger.info("Init V3 LLM Provider")

llm_provider = UniversalLLMProvider(
    openai_key=settings.OPENAI_API_KEY,
    anthropic_key=settings.ANTHROPIC_API_KEY
)



app = FastAPI(
    title="VideoCraft v3",
    description="The Pure Intelligence Layer",
    version="3.1.0"
)

v1_router = APIRouter(prefix="/api/v1", tags=["V1 Pipeline"])


@v1_router.post("/generate-plan")
async def v1_generate_plan():
    return {"message": "Here is your plan!"}

app.include_router(v1_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)


session 5
