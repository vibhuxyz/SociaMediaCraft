from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==========================================================
    # API Keys
    # ==========================================================
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    CUSTOM_API_KEY: str = ""
    CUSTOM_API_BASE: str = ""

    # ==========================================================
    # Infrastructure
    # ==========================================================
    REDIS_URL: str = "redis://localhost:6379"

    # ==========================================================
    # AI Engine
    # ==========================================================
    AI_ENGINE_USE_LLM: bool = True
    AI_ENGINE_LLM_TIMEOUT_SECONDS: float = 45.0

    # Default model if agent-specific model isn't configured
    # NOTE: temporarily pinned to OpenAI (gpt-4o-mini/gpt-4o) instead of OpenRouter's
    # free tier — OpenRouter is currently unreliable/unavailable. Switch back to the
    # openrouter/... presets below once that's resolved.
    AI_ENGINE_MODEL: str = "gpt-4o-mini"

    # Shared model presets
    FAST_MODEL: str = "gpt-4o-mini"
    SMART_MODEL: str = "gpt-4o"
    VALIDATOR_MODEL: str = "gpt-4o-mini"

    # ==========================================================
    # Planning Agents
    # ==========================================================

    MODEL_BRIEF_VALIDATOR: str = FAST_MODEL

    MODEL_DIRECTOR: str = SMART_MODEL

    MODEL_CLASSIFIER: str = FAST_MODEL

    MODEL_REQUIREMENT_ANALYZER: str = SMART_MODEL

    MODEL_MISSING_INFO_DETECTOR: str = FAST_MODEL

    MODEL_IMPORTANCE_SCORER: str = FAST_MODEL

    MODEL_CLARIFICATION_AGENT: str = SMART_MODEL

    MODEL_KNOWLEDGE_AGENT: str = FAST_MODEL

    # ==========================================================
    # Creative Planning
    # ==========================================================

    MODEL_CAMPAIGN_STRATEGY: str = FAST_MODEL

    MODEL_AUDIENCE_LOCALIZATION: str = FAST_MODEL

    MODEL_BRAND_IDENTITY: str = FAST_MODEL

    MODEL_CASTING_DIRECTOR: str = FAST_MODEL

    MODEL_CHARACTER_DESIGNER: str = FAST_MODEL

    MODEL_ENVIRONMENT_DESIGNER: str = FAST_MODEL

    MODEL_ART_DIRECTOR: str = FAST_MODEL

    MODEL_EMOTION_ANALYZER: str = FAST_MODEL

    MODEL_STORY_ARCHITECT: str = SMART_MODEL

    MODEL_SCREENPLAY_WRITER: str = FAST_MODEL

    MODEL_DIALOGUE_WRITER: str = FAST_MODEL

    MODEL_NARRATION_WRITER: str = FAST_MODEL

    MODEL_VOICE_DIRECTOR: str = FAST_MODEL

    MODEL_MUSIC_DIRECTOR: str = FAST_MODEL

    MODEL_SOUND_DESIGN_DIRECTOR: str = FAST_MODEL

    MODEL_STORYBOARD_DIRECTOR: str = FAST_MODEL

    MODEL_CINEMATOGRAPHY_DIRECTOR: str = FAST_MODEL

    MODEL_SHOT_PLANNER: str = SMART_MODEL

    MODEL_PROMPT_ENGINEERING: str = SMART_MODEL

    MODEL_ASSET_PLANNER: str = FAST_MODEL

    MODEL_QUALITY_REVIEW: str = SMART_MODEL

    # ==========================================================
    # Validation
    # ==========================================================

    MODEL_AGENT_VALIDATOR: str = VALIDATOR_MODEL

    # ==========================================================
    # Helpers
    # ==========================================================

    def model_for_agent(self, agent_name: str | None) -> str:
        if not agent_name:
            return self.AI_ENGINE_MODEL

        setting_name = f"MODEL_{agent_name.upper()}"
        return getattr(self, setting_name, self.AI_ENGINE_MODEL)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()  # type: ignore
