from providers.llm.universal_provider import UniversalLLMProvider
from config.settings import settings

llm_providers = UniversalLLMProvider(
    openai_key=settings.OPENAI_API_KEY,
    anthropic_key=settings.ANTHROPIC_API_KEY,
    openrouter_key=settings.OPENROUTER_API_KEY,
    custom_key=settings.CUSTOM_API_KEY,
    custom_base=settings.CUSTOM_API_BASE
)

# Global tracker for planning phase metrics
planning_metrics = {
    "total_time_sec": 0.0,
    "total_cost_usd": 0.0,
    "api_calls": 0
}
