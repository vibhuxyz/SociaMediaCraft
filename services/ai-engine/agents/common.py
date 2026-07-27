import json
import inspect
from pathlib import Path
from typing import Any, Type, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T", bound=BaseModel)


class DirectorPlan(BaseModel):
    project_type: str = "advertisement"
    subtype: str = "product_showcase"
    complexity: str = "medium"
    style: str = "luxury"
    duration: str = "30s"
    capabilities: list[str] = Field(
        default_factory=lambda: ["branding", "motion", "voice"],
        description="High-level capabilities required (e.g. dialogue, narration, motion, voice, branding, product, story)"
    )


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
    logo_rules: str = "Use logo clearly with safe margins when supplied. If no logo is provided, explicitly state that a text placeholder should be used."
    tagline: str = ""
    brand_mention_timing: str = "Must mention brand in first 5 seconds"


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


class StoryScene(BaseModel):
    scene_number: int
    setting: str
    action: str
    emotion: str


class StoryPlan(BaseModel):
    theme: str = "The central theme of the story."
    conflict: str = "The audience has an unmet need."
    resolution: str = "The project idea resolves that need."
    call_to_action: str = "Must include a strong, directive Call to Action in the final scene (e.g., 'Visit our website')."
    duration_limit: str = "Must strictly fit within 30 seconds."
    estimated_duration_seconds: int = 30
    scenes: list[StoryScene] = Field(
        default_factory=lambda: [
            StoryScene(scene_number=1, setting="Establishing location", action="Introduction", emotion="Curious"),
            StoryScene(scene_number=2, setting="Development location", action="Conflict presented", emotion="Engaged"),
            StoryScene(scene_number=3, setting="Resolution location", action="Final CTA", emotion="Confident"),
        ]
    )


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


class VoicePlan(BaseModel):
    has_dialogue: bool = False
    has_narration: bool = False
    requires_voice: bool = False
    captions_only: bool = False
    voice_provider: str = "ElevenLabs"
    voice_style: str = "Unspecified"
    speakers: list[str] = Field(default_factory=list, description="List of character IDs or names that will speak")

class DialogueLine(BaseModel):
    speaker: str
    line: str

class DialoguePlan(BaseModel):
    lines: list[DialogueLine] = Field(default_factory=list)

class NarrationBlock(BaseModel):
    scene_number: int
    text: str

class NarrationPlan(BaseModel):
    blocks: list[NarrationBlock] = Field(default_factory=list)

class AudioPlan(BaseModel):
    music_selection: str = "Stock music"
    foley_planning: list[str] = Field(default_factory=list)
    ambient_audio: str = "None"
    sound_effects: list[str] = Field(default_factory=list)
    voice_timing_strategy: str = "Follow visuals"
    audio_mix_strategy: str = "Balanced"


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


class CinematographySceneBreakdown(BaseModel):
    scene_number: int
    camera_direction: str

class CinematographyPlan(BaseModel):
    camera_movement: str = "Slow dolly and composed static frames"
    lighting_style: str = "Soft key with controlled highlights"
    composition_rules: str = "Clean center framing and rule of thirds"
    depth_of_field: str = "Moderate shallow focus"
    aspect_ratio: str = "16:9"
    scene_count: int = 3
    scene_breakdowns: list[CinematographySceneBreakdown] = Field(
        default_factory=lambda: [
            CinematographySceneBreakdown(scene_number=1, camera_direction="Wide establishing shot"),
            CinematographySceneBreakdown(scene_number=2, camera_direction="Medium tracking shot"),
            CinematographySceneBreakdown(scene_number=3, camera_direction="Close up locked off")
        ]
    )


class Shot(BaseModel):
    shot_id: str
    scene_number: int
    duration: str
    shot_type: str
    camera_movement: str
    transition_out: str
    action_description: str = Field(default="Base action description")
    complexity_score: int = Field(default=1)
    risky_interactions: list[str] = Field(default_factory=list)

class MicroAction(BaseModel):
    time: str = Field(description="Time window for this action (e.g. 0.0-0.5)")
    action: str = Field(description="The precise physical action happening in this time window")

class ShotMotionPlan(BaseModel):
    shot_id: str
    duration: str
    micro_actions: list[MicroAction] = Field(default_factory=list)

class MotionPlan(BaseModel):
    shot_motions: list[ShotMotionPlan] = Field(default_factory=list)


class ShotPlan(BaseModel):
    shots: list[Shot] = Field(
        default_factory=lambda: [
            Shot(shot_id="1A", scene_number=1, duration="5s", shot_type="Wide shot", camera_movement="Slow push in", transition_out="Cut"),
            Shot(shot_id="2A", scene_number=2, duration="8s", shot_type="Medium shot", camera_movement="Smooth tracking", transition_out="Match cut"),
            Shot(shot_id="3A", scene_number=3, duration="5s", shot_type="Close up", camera_movement="Locked off", transition_out="Fade out"),
        ]
    )




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
    generation_manifest: dict[str, Any] = Field(default_factory=dict)
    quality_report: dict[str, Any] = Field(default_factory=dict)
    cost_estimation: dict[str, Any] = Field(default_factory=dict)


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


def get_domain_knowledge(state: dict[str, Any], domains: list[str], agent_name: str | None = None) -> str:
    """Extracts and formats knowledge files relevant to specific domains, and prepends hard rules."""
    result_blocks = []
    
    if not agent_name:
        raw_name = infer_calling_agent_name()
        if raw_name:
            agent_name = raw_name.replace("_", " ").title()
            
    hard_rules = state.get("hard_rules", {})
    agent_rules = []
    if isinstance(hard_rules, dict) and agent_name:
        agent_rules = hard_rules.get(agent_name, [])
    elif isinstance(hard_rules, list):
        agent_rules = hard_rules
        
    if agent_rules:
        rules_text = "\n".join(f"- {rule}" for rule in agent_rules)
        result_blocks.append(f"--- STRICT DETERMINISTIC RULES ---\nYou MUST obey these rules exactly:\n{rules_text}\n")
    
    knowledge = state.get("knowledge", {})
    if knowledge:
        relevant_knowledge = []
        for filepath, content in knowledge.items():
            if any(filepath.startswith(domain) for domain in domains):
                relevant_knowledge.append(f"--- KNOWLEDGE: {filepath} ---\n{content}\n")
        
        if relevant_knowledge:
            result_blocks.append("--- CRITICAL DOMAIN KNOWLEDGE YOU MUST FOLLOW ---\n" + "\n".join(relevant_knowledge))
            
    return "\n\n".join(result_blocks)


class ValidationResult(BaseModel):
    is_valid: bool
    confidence_score: float
    feedback: str = "Output meets all constraints."


async def run_structured_agent(
    state: dict[str, Any],
    response_model: Type[T],
    description: str,
    fallback: T,
    agent_name: str | None = None,
    state_key: str | None = None,
    dependencies: list[str] | None = None,
) -> T:
    from config.settings import settings

    if not settings.AI_ENGINE_USE_LLM:
        return fallback

    resolved_agent_name = agent_name or infer_calling_agent_name()
    model = settings.model_for_agent(resolved_agent_name)
    agent_label = resolved_agent_name or response_model.__name__

    # Incremental Execution (Caching) Check
    invalidated = state.get("invalidated_nodes", [])
    if state_key and state_key in state and state.get(state_key) and agent_label not in invalidated:
        print(f"[AI ENGINE] {agent_label} -> ⚡ USING CACHED RESULT ({state_key})")
        
        cached_data = state[state_key]
        if isinstance(cached_data, dict):
            return response_model.model_validate(cached_data)
        elif isinstance(cached_data, response_model):
            return cached_data
        else:
            return response_model.model_validate(model_to_dict(cached_data))

    from dependencies import llm_providers
    
    max_retries = 2
    feedback_context = ""

    import time
    start_time = time.perf_counter()

    # Build Shared Immutable Context
    shared_context = {
        "user_prompt": state.get("prompt", ""),
        "director_plan": state.get("director_plan", {}),
        "requirements": state.get("requirements", {}),
        "campaign_strategy": state.get("campaign_strategy", {}),
    }
    
    # Build specific dependencies
    deps_context = {}
    if dependencies:
        for dep in dependencies:
            if dep in state:
                deps_context[dep] = state[dep]
                
    user_prompt_content = (
        "--- SHARED CONTEXT ---\n" + serialize_state(shared_context) + "\n\n"
    )
    if deps_context:
        user_prompt_content += "--- AGENT DEPENDENCIES ---\n" + serialize_state(deps_context) + "\n\n"

    for attempt in range(max_retries):
        try:
            prompt = description
            if feedback_context:
                prompt += f"\n\nPREVIOUS ATTEMPT FAILED VALIDATION:\n{feedback_context}\nFix the issues."
                
            output = await llm_providers.generate_structured_output(
                model=model,
                system_prompt=prompt,
                user_prompt=user_prompt_content,
                response_model=response_model,
                timeout=settings.AI_ENGINE_LLM_TIMEOUT_SECONDS,
            )
            
            # Validation Layer
            hard_rules_dict = state.get("hard_rules", {})
            agent_rules = []
            
            # Map folder name (e.g. story_architect) to Title Case (e.g. Story Architect)
            title_name = agent_label.replace("_", " ").title()
            if isinstance(hard_rules_dict, dict):
                agent_rules = hard_rules_dict.get(title_name, [])
            elif isinstance(hard_rules_dict, list):
                agent_rules = hard_rules_dict
                
            if agent_rules:
                val_prompt = (
                    f"You are a strict QA Validator for the {title_name} agent.\n"
                    "Your job is to check if the provided Agent Output (which is a PLANNING DOCUMENT, not the final video) violates ANY of these specific rules:\n"
                    + "\n".join(f"- {r}" for r in agent_rules)
                    + "\n\nCRITICAL CONTEXT FROM USER:\n"
                    + f"{state.get('clarification_answers', {})}\n\n"
                    "If a rule requires an asset (e.g. a logo) but the user explicitly stated they don't have it or don't want it, DO NOT fail the validation. "
                    "If the rule specifies a timing constraint (e.g. 'mention brand in first 5 seconds') or a duration limit, the Agent Output satisfies this rule if it EXPLICITLY STATES or COMMANDS that constraint within its generated text or variables. "
                    "You are validating that the Agent successfully INCLUDED the rule in its plan. "
                    "If it violates a rule and is not excused by the user's answers, set is_valid to false and provide feedback. "
                    "Rate your confidence (0.0 to 1.0) in the output's quality."
                )
                
                validation = await llm_providers.generate_structured_output(
                    model="gpt-4o-mini", # Use fast model for validation
                    system_prompt=val_prompt,
                    user_prompt=f"AGENT OUTPUT TO VALIDATE:\n{output.model_dump_json(indent=2)}",
                    response_model=ValidationResult,
                    timeout=10,
                )
                
                if validation.confidence_score < 0.75 or not validation.is_valid:
                    print(f"[AI ENGINE] {title_name} validation failed (Confidence: {validation.confidence_score}): {validation.feedback}")
                    feedback_context = validation.feedback
                    continue # Retry
                elif validation.confidence_score < 0.90:
                    print(f"[AI ENGINE] {title_name} generated a warning (Confidence: {validation.confidence_score}): {validation.feedback}. Proceeding anyway.")
            
            end_time = time.perf_counter()
            print(f"[PROFILE] {title_name:<25} | {end_time - start_time:5.2f}s | Retries: {attempt}")
            
            return output
        except Exception as exc:
            print(f"[AI ENGINE] Exception for {agent_label} using {model}: {exc}")
            if attempt == max_retries - 1:
                end_time = time.perf_counter()
                print(f"[PROFILE] {agent_label.title():<25} | {end_time - start_time:5.2f}s | Retries: {attempt} (FAILED)")
                return fallback
                
    end_time = time.perf_counter()
    print(f"[PROFILE] {agent_label.title():<25} | {end_time - start_time:5.2f}s | Retries: {max_retries} (FALLBACK)")
    return fallback

class KnowledgeSelectorPlan(BaseModel):
    selected_files: list[str] = Field(default_factory=list)

