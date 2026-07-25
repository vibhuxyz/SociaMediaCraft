import json
import inspect
from pathlib import Path
from typing import Any, Type, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T", bound=BaseModel)


class DirectorPlan(BaseModel):
    genre: str = "Commercial"
    purpose: str = "Promote the idea clearly"
    target_audience: str = "General audience"
    tone: str = "Cinematic"
    duration: str = "60s"
    style: str = "Modern"
    references: list[str] = Field(default_factory=list)


class ClassifierPlan(BaseModel):
    project_type: str = "Commercial"
    confidence: float = 0.75
    rationale: str = "Inferred from the prompt."


class KnownRequirement(BaseModel):
    name: str
    value: str


class RequirementAnalysisPlan(BaseModel):
    known: list[KnownRequirement] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)


class BriefValidationPlan(BaseModel):
    is_valid: bool = True
    validation_error: str | None = None
    warnings: list[str] = Field(default_factory=list)


class MissingInformationPlan(BaseModel):
    missing_information: list[str] = Field(default_factory=list)


class MissingFieldDecision(BaseModel):
    field: str
    impact: str = "Low"
    action: str = "Use defaults"


class ImportanceScorerPlan(BaseModel):
    decisions: list[MissingFieldDecision] = Field(default_factory=list)


class ClarificationPlan(BaseModel):
    questions: list[str] = Field(default_factory=list)


class KnowledgeResearchPlan(BaseModel):
    brand_guidelines_summary: str = "No external brand guidelines supplied."
    visual_rules: list[str] = Field(default_factory=list)
    campaign_references: list[str] = Field(default_factory=list)


class CampaignStrategy(BaseModel):
    goal: str = "Awareness"
    primary_emotion: str = "Interest"
    call_to_action: str = "Learn more"
    core_message: str = "A clear, memorable message."


class AudienceLocalizationPlan(BaseModel):
    country: str = "Global"
    language: str = "English"
    accent: str = "Neutral"
    culture: str = "Broadly accessible"
    legal_rules: list[str] = Field(default_factory=lambda: ["Avoid misleading claims"])


class BrandIdentityPlan(BaseModel):
    brand_personality: str = "Modern and trustworthy"
    color_palette: list[str] = Field(default_factory=lambda: ["black", "white", "accent color"])
    typography: str = "Clean sans-serif"
    logo_rules: str = "Use logo clearly with safe margins when supplied."
    tagline: str = ""


class CharacterCasting(BaseModel):
    role_name: str = "Lead"
    gender: str = "Unspecified"
    ethnicity: str = "Unspecified"
    age: str = "Adult"
    archetype: str = "Relatable protagonist"
    build: str = "Natural"


class CastingPlan(BaseModel):
    cast: list[CharacterCasting] = Field(default_factory=lambda: [CharacterCasting()])


class CharacterAppearance(BaseModel):
    face: str = "Natural, expressive face"
    hair: str = "Neat styling"
    eyes: str = "Expressive"


class CharacterSheet(BaseModel):
    name: str = "Lead"
    appearance: CharacterAppearance = Field(default_factory=CharacterAppearance)
    outfits: list[str] = Field(default_factory=lambda: ["Clean, camera-ready outfit"])
    accessories: list[str] = Field(default_factory=list)


class CharacterDesignPlan(BaseModel):
    character_sheets: list[CharacterSheet] = Field(default_factory=lambda: [CharacterSheet()])


class Location(BaseModel):
    name: str = "Primary location"
    architecture: str = "Contemporary"
    weather: str = "Clear"
    lighting: str = "Soft cinematic lighting"
    time_of_day: str = "Golden hour"
    key_props: list[str] = Field(default_factory=list)


class EnvironmentDesignPlan(BaseModel):
    locations: list[Location] = Field(default_factory=lambda: [Location()])


class ArtDirectionPlan(BaseModel):
    visual_style: str = "Cinematic realism"
    camera_type: str = "Digital cinema camera"
    lens: str = "35mm and 50mm primes"
    film_stock: str = "Clean digital"
    color_grading: str = "Natural contrast"
    mood: str = "Polished"


class EmotionPlan(BaseModel):
    opening: str = "Curiosity"
    middle: str = "Engagement"
    ending: str = "Confidence"
    primary_emotion: str = "Trust"


class StoryPlan(BaseModel):
    beginning: str = "Introduce the subject and context."
    middle: str = "Show the central transformation or benefit."
    ending: str = "Close with a memorable resolution."
    conflict: str = "The audience has an unmet need."
    resolution: str = "The project idea resolves that need."
    scene_summary: list[str] = Field(default_factory=lambda: ["Opening", "Development", "Final CTA"])


class ScreenplayScene(BaseModel):
    scene_number: int
    slugline: str
    action_lines: str


class ScreenplayPlan(BaseModel):
    scenes: list[ScreenplayScene] = Field(
        default_factory=lambda: [
            ScreenplayScene(scene_number=1, slugline="INT/EXT - PRIMARY LOCATION - DAY", action_lines="The idea is introduced visually."),
            ScreenplayScene(scene_number=2, slugline="INT/EXT - PRIMARY LOCATION - LATER", action_lines="The core benefit becomes clear."),
            ScreenplayScene(scene_number=3, slugline="INT/EXT - PRIMARY LOCATION - END", action_lines="The film resolves with a clear final image."),
        ]
    )


class DialogueLine(BaseModel):
    character_name: str
    emotion: str
    text: str


class DialoguePlan(BaseModel):
    has_dialogue: bool = False
    lines: list[DialogueLine] = Field(default_factory=list)


class NarrationBlock(BaseModel):
    scene_number: int
    text: str
    tone_indicator: str


class NarrationPlan(BaseModel):
    has_narration: bool = True
    blocks: list[NarrationBlock] = Field(
        default_factory=lambda: [
            NarrationBlock(scene_number=1, text="A new possibility begins here.", tone_indicator="calm"),
            NarrationBlock(scene_number=2, text="Built for moments that matter.", tone_indicator="confident"),
            NarrationBlock(scene_number=3, text="Take the next step today.", tone_indicator="clear"),
        ]
    )


class VoicePlan(BaseModel):
    provider: str = "ElevenLabs"
    gender: str = "Unspecified"
    accent: str = "Neutral"
    emotion: str = "Confident"
    pace: str = "Medium"


class MusicPlan(BaseModel):
    genre: str = "Cinematic commercial"
    tempo: str = "90 BPM"
    mood: str = "Uplifting"
    instruments: list[str] = Field(default_factory=lambda: ["piano", "strings", "soft percussion"])
    ending_build: bool = True


class SoundDesignPlan(BaseModel):
    ambient: list[str] = Field(default_factory=lambda: ["subtle room tone"])
    foley: list[str] = Field(default_factory=lambda: ["soft movement"])
    sfx: list[str] = Field(default_factory=lambda: ["gentle transition whoosh"])


class StoryboardScene(BaseModel):
    scene_number: int
    visual_description: str
    keyframe_concept: str


class StoryboardPlan(BaseModel):
    storyboards: list[StoryboardScene] = Field(
        default_factory=lambda: [
            StoryboardScene(scene_number=1, visual_description="A polished opening image establishes the world.", keyframe_concept="hero opening frame"),
            StoryboardScene(scene_number=2, visual_description="The subject interacts with the central idea.", keyframe_concept="benefit reveal"),
            StoryboardScene(scene_number=3, visual_description="A final composition supports the call to action.", keyframe_concept="closing brand frame"),
        ]
    )


class CinematographyPlan(BaseModel):
    camera_movement: str = "Slow dolly and composed static frames"
    lighting_style: str = "Soft key with controlled highlights"
    composition_rules: str = "Clean center framing and rule of thirds"
    depth_of_field: str = "Moderate shallow focus"


class Shot(BaseModel):
    shot_id: str
    scene_number: int
    duration: str
    shot_type: str
    camera_movement: str
    transition_out: str


class ShotPlan(BaseModel):
    shots: list[Shot] = Field(
        default_factory=lambda: [
            Shot(shot_id="1A", scene_number=1, duration="5s", shot_type="Wide shot", camera_movement="Slow push in", transition_out="Cut"),
            Shot(shot_id="2A", scene_number=2, duration="8s", shot_type="Medium shot", camera_movement="Smooth tracking", transition_out="Match cut"),
            Shot(shot_id="3A", scene_number=3, duration="5s", shot_type="Close up", camera_movement="Locked off", transition_out="Fade out"),
        ]
    )


class OptimizedPrompt(BaseModel):
    target_engine: str
    prompt_text: str


class PromptEngineeringPlan(BaseModel):
    image_prompts: list[OptimizedPrompt] = Field(default_factory=list)
    video_prompts: list[OptimizedPrompt] = Field(default_factory=list)
    audio_prompts: list[OptimizedPrompt] = Field(default_factory=list)


class AssetPlan(BaseModel):
    total_images_required: int = 3
    total_video_clips_required: int = 3
    total_voice_tracks: int = 1
    total_music_tracks: int = 1
    total_sfx: int = 3
    needs_thumbnail: bool = True


class QualityReviewPlan(BaseModel):
    story_consistency_pass: bool = True
    character_consistency_pass: bool = True
    brand_consistency_pass: bool = True
    readiness_score: int = 80
    final_approval: bool = True
    feedback: str = "Plan is ready for generation."


class CreativePlan(BaseModel):
    metadata: dict[str, Any] = Field(default_factory=dict)
    project: dict[str, Any] = Field(default_factory=dict)
    project_type: str = "Commercial"
    director: dict[str, Any] = Field(default_factory=dict)
    campaign_strategy: dict[str, Any] = Field(default_factory=dict)
    audience_localization: dict[str, Any] = Field(default_factory=dict)
    brand_identity: dict[str, Any] = Field(default_factory=dict)
    requirements: dict[str, Any] = Field(default_factory=dict)
    casting: dict[str, Any] = Field(default_factory=dict)
    characters: dict[str, Any] = Field(default_factory=dict)
    environment: dict[str, Any] = Field(default_factory=dict)
    art_direction: dict[str, Any] = Field(default_factory=dict)
    emotion: dict[str, Any] = Field(default_factory=dict)
    story: dict[str, Any] = Field(default_factory=dict)
    screenplay: dict[str, Any] = Field(default_factory=dict)
    dialogue: dict[str, Any] = Field(default_factory=dict)
    narration: dict[str, Any] = Field(default_factory=dict)
    voice_plan: dict[str, Any] = Field(default_factory=dict)
    music_plan: dict[str, Any] = Field(default_factory=dict)
    sound_design: dict[str, Any] = Field(default_factory=dict)
    storyboard: dict[str, Any] = Field(default_factory=dict)
    cinematography: dict[str, Any] = Field(default_factory=dict)
    shot_plan: dict[str, Any] = Field(default_factory=dict)
    prompt_pack: dict[str, Any] = Field(default_factory=dict)
    asset_plan: dict[str, Any] = Field(default_factory=dict)
    quality_report: dict[str, Any] = Field(default_factory=dict)


def model_to_dict(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, list):
        return [model_to_dict(item) for item in value]
    if isinstance(value, dict):
        return {key: model_to_dict(item) for key, item in value.items()}
    return value


def serialize_state(state: dict[str, Any]) -> str:
    return json.dumps(model_to_dict(dict(state)), indent=2, default=str)


def infer_project_type(prompt: str) -> str:
    lowered = prompt.lower()
    if any(word in lowered for word in ["ad", "advert", "commercial", "product", "brand"]):
        return "Commercial"
    if any(word in lowered for word in ["story", "film", "short", "scene"]):
        return "Story Film"
    if "travel" in lowered:
        return "Travel Reel"
    if "music video" in lowered:
        return "Music Video"
    return "Commercial"


def infer_calling_agent_name() -> str | None:
    for frame_info in inspect.stack()[1:]:
        path = Path(frame_info.filename)
        if "agents" in path.parts and path.name == "node.py":
            return path.parent.name
    return None


async def run_structured_agent(
    state: dict[str, Any],
    response_model: Type[T],
    description: str,
    fallback: T,
    agent_name: str | None = None,
) -> T:
    from config.settings import settings

    if not settings.AI_ENGINE_USE_LLM:
        return fallback

    from dependencies import llm_providers

    resolved_agent_name = agent_name or infer_calling_agent_name()
    model = settings.model_for_agent(resolved_agent_name)
    agent_label = resolved_agent_name or response_model.__name__

    try:
        print(f"[AI ENGINE] {agent_label} -> {model}")
        return await llm_providers.generate_structured_output(
            model=model,
            system_prompt=description,
            user_prompt=f"CURRENT CREATIVE STATE:\n{serialize_state(state)}",
            response_model=response_model,
            timeout=settings.AI_ENGINE_LLM_TIMEOUT_SECONDS,
        )
    except Exception as exc:
        print(f"[AI ENGINE] Falling back for {agent_label} using {model}: {exc}")
        return fallback
