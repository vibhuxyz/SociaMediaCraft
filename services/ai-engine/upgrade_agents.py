import os

agents_data = {
    "importance_scorer": {
        "schema_name": "ImportanceScorerPlan",
        "schema_code": """from pydantic import BaseModel, Field

class MissingFieldDecision(BaseModel):
    field: str = Field(description="The missing field in question")
    impact: str = Field(description="Impact of missing this info: 'Low' or 'High'")
    action: str = Field(description="Action to take: 'Use defaults' or 'Ask user'")

class ImportanceScorerPlan(BaseModel):
    decisions: list[MissingFieldDecision] = Field(description="List of decisions for each missing field")
""",
        "description": "Evaluate missing information and decide if user input is strictly required or if AI defaults can be used.",
    },
    "clarification_agent": {
        "schema_name": "ClarificationPlan",
        "schema_code": """from pydantic import BaseModel, Field

class ClarificationPlan(BaseModel):
    questions: list[str] = Field(description="Dynamic, contextual interview questions to ask the user to fill in critical missing information.")
""",
        "description": "Generate dynamic interview questions for the user to resolve critical missing creative information.",
    },
    "knowledge_agent": {
        "schema_name": "KnowledgeResearchPlan",
        "schema_code": """from pydantic import BaseModel, Field

class KnowledgeResearchPlan(BaseModel):
    brand_guidelines_summary: str = Field(description="Summary of applied brand guidelines")
    visual_rules: list[str] = Field(description="Rules for logos, colors, and placement")
    campaign_references: list[str] = Field(description="Insights from previous campaigns or chosen templates")
""",
        "description": "Parse brand guidelines, logos, and previous campaigns to build foundational knowledge for the video.",
    },
    "audience_localization": {
        "schema_name": "AudienceLocalizationPlan",
        "schema_code": """from pydantic import BaseModel, Field

class AudienceLocalizationPlan(BaseModel):
    country: str = Field(description="Target country")
    language: str = Field(description="Target language")
    accent: str = Field(description="Preferred accent")
    culture: str = Field(description="Cultural nuances or festivals to include")
    legal_rules: list[str] = Field(description="Regional compliance or safe guidelines (e.g., Meta Safe)")
""",
        "description": "Define the target audience, culture, language, and localization rules.",
    },
    "brand_identity": {
        "schema_name": "BrandIdentityPlan",
        "schema_code": """from pydantic import BaseModel, Field

class BrandIdentityPlan(BaseModel):
    brand_personality: str = Field(description="The persona of the brand (e.g., Luxury, Elegant, Playful)")
    color_palette: list[str] = Field(description="Hex codes or color descriptions")
    typography: str = Field(description="Font families and styles")
    logo_rules: str = Field(description="Rules for logo placement and animation")
    tagline: str = Field(description="Official brand tagline to be used")
""",
        "description": "Lock in the brand personality, color palette, typography, and logo rules.",
    },
    "casting_director": {
        "schema_name": "CastingPlan",
        "schema_code": """from pydantic import BaseModel, Field

class CharacterCasting(BaseModel):
    role_name: str = Field(description="Name or title of the role")
    gender: str = Field(description="Gender of the character")
    ethnicity: str = Field(description="Ethnicity or nationality")
    age: str = Field(description="Age range")
    archetype: str = Field(description="Character archetype (e.g., Luxury CEO, Rebel)")
    build: str = Field(description="Physique and build")

class CastingPlan(BaseModel):
    cast: list[CharacterCasting] = Field(description="List of all characters to be cast")
""",
        "description": "Define the gender, ethnicity, age, archetype, and build for all characters in the production.",
    },
    "character_designer": {
        "schema_name": "CharacterDesignPlan",
        "schema_code": """from pydantic import BaseModel, Field

class CharacterAppearance(BaseModel):
    face: str = Field(description="Facial features")
    hair: str = Field(description="Hair style and color")
    eyes: str = Field(description="Eye color and shape")

class CharacterSheet(BaseModel):
    name: str = Field(description="Character name")
    appearance: CharacterAppearance = Field(description="Physical appearance details")
    outfits: list[str] = Field(description="List of clothing outfits for different scenes")
    accessories: list[str] = Field(description="Key accessories")

class CharacterDesignPlan(BaseModel):
    character_sheets: list[CharacterSheet] = Field(description="Detailed visual sheets for all characters")
""",
        "description": "Create detailed, reusable character visual sheets including appearance and wardrobe.",
    },
    "environment_designer": {
        "schema_name": "EnvironmentDesignPlan",
        "schema_code": """from pydantic import BaseModel, Field

class Location(BaseModel):
    name: str = Field(description="Name of the location")
    architecture: str = Field(description="Architectural style")
    weather: str = Field(description="Weather conditions")
    lighting: str = Field(description="General lighting setup")
    time_of_day: str = Field(description="Time of day")
    key_props: list[str] = Field(description="Important props or furniture in the scene")

class EnvironmentDesignPlan(BaseModel):
    locations: list[Location] = Field(description="List of all locations built for the production")
""",
        "description": "Build the physical world, defining locations, architecture, weather, and key props.",
    },
    "art_director": {
        "schema_name": "ArtDirectionPlan",
        "schema_code": """from pydantic import BaseModel, Field

class ArtDirectionPlan(BaseModel):
    visual_style: str = Field(description="Overall visual style (e.g., Cinematic, Vintage, Cyberpunk)")
    camera_type: str = Field(description="Simulated camera equipment")
    lens: str = Field(description="Lens choices (e.g., 35mm, Anamorphic)")
    film_stock: str = Field(description="Film stock simulation")
    color_grading: str = Field(description="Color grading profile (e.g., Teal and Orange, Muted)")
    mood: str = Field(description="Overall aesthetic mood")
""",
        "description": "Create the overarching visual style, simulated camera choices, and color grading.",
    },
    "emotion_analyzer": {
        "schema_name": "EmotionPlan",
        "schema_code": """from pydantic import BaseModel, Field

class EmotionPlan(BaseModel):
    opening: str = Field(description="Emotional state at the start")
    middle: str = Field(description="Emotional state in the middle/climax")
    ending: str = Field(description="Emotional state at the resolution")
    primary_emotion: str = Field(description="The dominant emotion of the entire piece")
""",
        "description": "Map the emotional progression of the video from beginning to end.",
    },
    "screenplay_writer": {
        "schema_name": "ScreenplayPlan",
        "schema_code": """from pydantic import BaseModel, Field

class Scene(BaseModel):
    scene_number: int = Field(description="Scene sequence number")
    slugline: str = Field(description="INT/EXT - LOCATION - TIME")
    action_lines: str = Field(description="What is physically happening in the scene")

class ScreenplayPlan(BaseModel):
    scenes: list[Scene] = Field(description="Complete scene-by-scene breakdown of the video")
""",
        "description": "Write the scene-by-scene breakdown, sluglines, and action lines based on the story.",
    },
    "dialogue_writer": {
        "schema_name": "DialoguePlan",
        "schema_code": """from pydantic import BaseModel, Field

class DialogueLine(BaseModel):
    character_name: str = Field(description="Character speaking")
    emotion: str = Field(description="How it is spoken")
    text: str = Field(description="The actual spoken dialogue")

class DialoguePlan(BaseModel):
    has_dialogue: bool = Field(description="True if the video features spoken dialogue")
    lines: list[DialogueLine] = Field(description="Chronological list of dialogue lines")
""",
        "description": "Write natural, culturally appropriate dialogue for characters, or explicitly determine if no dialogue is needed.",
    },
    "narration_writer": {
        "schema_name": "NarrationPlan",
        "schema_code": """from pydantic import BaseModel, Field

class NarrationBlock(BaseModel):
    scene_number: int = Field(description="Which scene this voiceover plays over")
    text: str = Field(description="The voiceover text")
    tone_indicator: str = Field(description="Tone or emotion for the voice actor")

class NarrationPlan(BaseModel):
    has_narration: bool = Field(description="True if a voiceover is used")
    blocks: list[NarrationBlock] = Field(description="Blocks of narration mapped to scenes")
""",
        "description": "Write the professional voiceover scripts and map them to scenes.",
    },
    "voice_director": {
        "schema_name": "VoicePlan",
        "schema_code": """from pydantic import BaseModel, Field

class VoicePlan(BaseModel):
    provider: str = Field(description="Preferred AI voice provider (e.g., ElevenLabs)")
    gender: str = Field(description="Gender of the voiceover artist")
    accent: str = Field(description="Accent or dialect")
    emotion: str = Field(description="Primary emotion of the read")
    pace: str = Field(description="Speaking pace (e.g., Slow, Fast, Conversational)")
""",
        "description": "Plan the technical specifications for AI voice generation including provider, accent, and pace.",
    },
    "music_director": {
        "schema_name": "MusicPlan",
        "schema_code": """from pydantic import BaseModel, Field

class MusicPlan(BaseModel):
    genre: str = Field(description="Musical genre (e.g., Cinematic, Lo-Fi, Orchestral)")
    tempo: str = Field(description="Tempo description or BPM range")
    mood: str = Field(description="Musical mood (e.g., Uplifting, Suspenseful)")
    instruments: list[str] = Field(description="Key instruments to feature")
    ending_build: bool = Field(description="Whether the track should climax at the end")
""",
        "description": "Plan the musical score, defining genre, tempo, instruments, and mood.",
    },
    "sound_design_director": {
        "schema_name": "SoundDesignPlan",
        "schema_code": """from pydantic import BaseModel, Field

class SoundDesignPlan(BaseModel):
    ambient: list[str] = Field(description="Ambient sounds / room tone (e.g., wind, city traffic)")
    foley: list[str] = Field(description="Foley sounds (e.g., footsteps, fabric rustling)")
    sfx: list[str] = Field(description="Special sound effects (e.g., whooshes, impacts, digital glitches)")
""",
        "description": "Plan all non-music audio elements including ambient sound, foley, and SFX.",
    },
    "storyboard_director": {
        "schema_name": "StoryboardPlan",
        "schema_code": """from pydantic import BaseModel, Field

class StoryboardScene(BaseModel):
    scene_number: int = Field(description="Associated scene number")
    visual_description: str = Field(description="Highly descriptive visual prompt for what is seen")
    keyframe_concept: str = Field(description="The defining image/frame for this scene")

class StoryboardPlan(BaseModel):
    storyboards: list[StoryboardScene] = Field(description="Visual breakdown of every scene")
""",
        "description": "Translate the screenplay into visual storyboard concepts and keyframes for every scene.",
    },
    "cinematography_director": {
        "schema_name": "CinematographyPlan",
        "schema_code": """from pydantic import BaseModel, Field

class CinematographyPlan(BaseModel):
    camera_movement: str = Field(description="Global camera movement style (e.g., Handheld, Steadicam, Slow Dolly)")
    lighting_style: str = Field(description="Global lighting style (e.g., High Key, Chiaroscuro)")
    composition_rules: str = Field(description="Rules for framing (e.g., Rule of Thirds, Center Framed)")
    depth_of_field: str = Field(description="Expected depth of field (e.g., Shallow, Deep Focus)")
""",
        "description": "Establish the overarching camera movement, lighting, and composition rules for the production.",
    },
    "shot_planner": {
        "schema_name": "ShotPlan",
        "schema_code": """from pydantic import BaseModel, Field

class Shot(BaseModel):
    shot_id: str = Field(description="Unique shot identifier (e.g., 1A)")
    scene_number: int = Field(description="Which scene this shot belongs to")
    duration: str = Field(description="Estimated duration (e.g., 4s)")
    shot_type: str = Field(description="Type of shot (e.g., Close Up, Wide Shot)")
    camera_movement: str = Field(description="Specific camera movement for this shot")
    transition_out: str = Field(description="How this shot transitions to the next (e.g., Cut, Fade, Match Cut)")

class ShotPlan(BaseModel):
    shots: list[Shot] = Field(description="Exhaustive list of every shot needed for rendering")
""",
        "description": "Expand storyboard scenes into an exact, executable list of specific camera shots with durations.",
    },
    "prompt_engineering": {
        "schema_name": "PromptEngineeringPlan",
        "schema_code": """from pydantic import BaseModel, Field

class OptimizedPrompt(BaseModel):
    target_engine: str = Field(description="Which engine this is for (e.g., FLUX, Veo, Luma)")
    prompt_text: str = Field(description="The highly optimized, raw prompt string ready for API execution")

class PromptEngineeringPlan(BaseModel):
    image_prompts: list[OptimizedPrompt] = Field(description="Prompts optimized for image generation")
    video_prompts: list[OptimizedPrompt] = Field(description="Prompts optimized for video generation")
    audio_prompts: list[OptimizedPrompt] = Field(description="Prompts optimized for audio/music generation")
""",
        "description": "Convert creative plans into highly optimized, model-specific prompts (FLUX, Veo, ElevenLabs, etc.).",
    },
    "asset_planner": {
        "schema_name": "AssetPlan",
        "schema_code": """from pydantic import BaseModel, Field

class AssetPlan(BaseModel):
    total_images_required: int = Field(description="Number of still images needed")
    total_video_clips_required: int = Field(description="Number of video clips needed")
    total_voice_tracks: int = Field(description="Number of voiceover tracks")
    total_music_tracks: int = Field(description="Number of music tracks")
    total_sfx: int = Field(description="Number of sound effects")
    needs_thumbnail: bool = Field(description="Whether a custom thumbnail must be generated")
""",
        "description": "Calculate and tabulate the exact numerical requirements of all digital assets needed before rendering.",
    },
    "quality_review": {
        "schema_name": "QualityReviewPlan",
        "schema_code": """from pydantic import BaseModel, Field

class QualityReviewPlan(BaseModel):
    story_consistency_pass: bool = Field(description="Is the story logical and consistent?")
    character_consistency_pass: bool = Field(description="Are characters consistent?")
    brand_consistency_pass: bool = Field(description="Are brand guidelines met?")
    readiness_score: int = Field(description="Score out of 100 for production readiness")
    final_approval: bool = Field(description="True if the plan is cleared to proceed to V4 Rendering")
    feedback: str = Field(description="Detailed feedback or warnings if approval is denied")
""",
        "description": "Perform a final, comprehensive quality check on the entire production plan before clearing it for generation.",
    }
}

base_dir = "/Users/vibhu/Coding/omni-ai-platform/services/ai-engine/agents"

for agent_folder, data in agents_data.items():
    agent_path = os.path.join(base_dir, agent_folder)
    schema_name = data["schema_name"]
    schema_code = data["schema_code"]
    description = data["description"]
    
    if not os.path.exists(agent_path):
        os.makedirs(agent_path, exist_ok=True)
    
    # Write Production Schema
    with open(os.path.join(agent_path, "schema.py"), "w") as f:
        f.write(schema_code)

    # Write Production Node
    node_code = f'''import json
from workflow.state import CreativeState
from agents.{agent_folder}.schema import {schema_name}
from dependencies import llm_providers

async def {agent_folder}_node(state: CreativeState):
    print("🎬 [{agent_folder.upper()}] is analyzing the current state...")
    
    # Serialize state context to give the LLM full visibility, excluding any non-serializable objects
    context_dict = {{k: v for k, v in state.items() if isinstance(v, (str, int, float, bool, list, dict))}}
    try:
        # Convert Pydantic models to dict if they are in state
        for key, value in state.items():
            if hasattr(value, "model_dump"):
                context_dict[key] = value.model_dump()
            elif hasattr(value, "dict"):
                context_dict[key] = value.dict()
        context_str = json.dumps(context_dict, indent=2)
    except Exception as e:
        context_str = str(state)

    system_prompt = (
        "You are the {agent_folder.replace('_', ' ').title()}. "
        "{description}\\n\\n"
        "You have full access to the creative state up to this point. "
        "Analyze the provided context and fulfill your specific responsibilities."
    )

    plan = await llm_providers.run_with_tools(
        model="gpt-4o-mini",
        system_prompt=system_prompt,
        user_prompt=f"CURRENT CREATIVE STATE:\\n{{context_str}}\\n\\nPlease generate the {schema_name}.",
        response_model={schema_name}
    )

    return {{"{agent_folder}_plan": plan}}
'''
    with open(os.path.join(agent_path, "node.py"), "w") as f:
        f.write(node_code)

print("Production-level upgrade complete for all agents!")
