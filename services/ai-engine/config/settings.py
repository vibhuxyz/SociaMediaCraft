from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    gemini_api_key: str = ""
    AI_ENGINE_USE_LLM: bool = True
    AI_ENGINE_MODEL: str = "gpt-4o-mini"
    AI_ENGINE_LLM_TIMEOUT_SECONDS: float = 45.0

    MODEL_BRIEF_VALIDATOR: str = "gpt-4o-mini"
    MODEL_DIRECTOR: str = "gpt-4o-mini"
    MODEL_CLASSIFIER: str = "gpt-4o-mini"
    MODEL_REQUIREMENT_ANALYZER: str = "gpt-4o-mini"
    MODEL_MISSING_INFO_DETECTOR: str = "gpt-4o-mini"
    MODEL_IMPORTANCE_SCORER: str = "gpt-4o-mini"
    MODEL_CLARIFICATION_AGENT: str ="gpt-4o-mini"
    MODEL_KNOWLEDGE_AGENT: str ="gpt-4o-mini"
    MODEL_CAMPAIGN_STRATEGY: str = "gpt-4o-mini"
    MODEL_AUDIENCE_LOCALIZATION: str ="gpt-4o-mini"
    MODEL_BRAND_IDENTITY: str = "gpt-4o-mini"
    MODEL_CASTING_DIRECTOR: str = "gpt-4o-mini"
    MODEL_CHARACTER_DESIGNER: str = "gpt-4o-mini"
    MODEL_ENVIRONMENT_DESIGNER: str = "gpt-4o-mini"
    MODEL_ART_DIRECTOR: str = "gpt-4o-mini"
    MODEL_EMOTION_ANALYZER: str = "gpt-4o-mini"
    MODEL_STORY_ARCHITECT: str = "gpt-4o-mini"
    MODEL_SCREENPLAY_WRITER: str ="gpt-4o-mini"
    MODEL_DIALOGUE_WRITER: str = "gpt-4o-mini"
    MODEL_NARRATION_WRITER: str ="gpt-4o-mini"
    MODEL_VOICE_DIRECTOR: str ="gpt-4o-mini"
    MODEL_MUSIC_DIRECTOR: str = "gpt-4o-mini"
    MODEL_SOUND_DESIGN_DIRECTOR: str ="gpt-4o-mini"
    MODEL_STORYBOARD_DIRECTOR: str = "gpt-4o-mini"
    MODEL_CINEMATOGRAPHY_DIRECTOR: str = "gpt-4o-mini"
    MODEL_SHOT_PLANNER: str = "gpt-4o-mini"
    MODEL_PROMPT_ENGINEERING: str = "gpt-4o-mini"
    MODEL_ASSET_PLANNER: str = "gpt-4o-mini"
    MODEL_QUALITY_REVIEW: str = "gpt-4o-mini"

    def model_for_agent(self, agent_name: str | None) -> str:
        if not agent_name:
            return self.AI_ENGINE_MODEL

        setting_name = f"MODEL_{agent_name.upper()}"
        configured_model = getattr(self, setting_name, "")
        return configured_model or self.AI_ENGINE_MODEL
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings() # type:ignore
