from providers.llm.universal_provider import UniversalLLMProvider
from config.settings import settings

# A single shared instance of our LLM provider that all agents can import
llm_providers = UniversalLLMProvider(
    openai_key=settings.OPENAI_API_KEY,
    anthropic_key=settings.ANTHROPIC_API_KEY
)
