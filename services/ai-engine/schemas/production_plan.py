from typing import List, Optional
from pydantic import BaseModel, Field

# ------------------------------------------------------------------
# Structured Output Definitions using Pydantic
# ------------------------------------------------------------------

class Character(BaseModel):
    name: str = Field(description="The name of the character.")
    description: str = Field(description="Visual description of the character for image generation.")
    voice_profile: str = Field(description="Description of how their voice should sound (e.g., raspy, deep, energetic).")

class MicroAction(BaseModel):
    time: str = Field(description="Time window for this action (e.g. 0.0-0.5)")
    action: str = Field(description="The precise physical action happening in this time window")

class Shot(BaseModel):
    shot_id: str = Field(description="Sequential ID of the shot. Can be alphanumeric if split (e.g., 4A, 4B).")
    camera_angle: str = Field(description="The camera angle (e.g., Close-up, Wide Shot).")
    action_description: str = Field(description="What is happening visually in this specific shot.")
    dialogue: Optional[str] = Field(default=None, description="Any dialogue spoken during this shot.")
    estimated_duration: float = Field(description="Estimated duration of the shot in seconds.")
    complexity_score: int = Field(default=1, description="Action complexity score (1-10).")
    risky_interactions: List[str] = Field(default_factory=list, description="List of risky hand-object interactions detected.")
    micro_actions: List[MicroAction] = Field(default_factory=list, description="Chronological sequence of specific physical micro-actions.")

class Scene(BaseModel):
    scene_id: int = Field(description="Sequential ID of the scene.")
    setting: str = Field(description="The physical setting of the scene.")
    time_of_day: str = Field(description="Time of day (e.g., Morning, Night).")
    shots: List[Shot] = Field(description="The sequence of shots that make up this scene.")

class ProductionPlan(BaseModel):
    """
    The ultimate structured output we want the LLM to generate based on a user prompt.
    This acts as the blueprint for the Worker to start rendering.
    """
    title: str = Field(description="A catchy title for the generated video.")
    characters: List[Character] = Field(description="List of characters appearing in the video.")
    scenes: List[Scene] = Field(description="The scenes broken down into individual renderable shots.")
    overall_vibe: str = Field(description="The emotional tone or vibe (e.g., cyberpunk, dark, uplifting).")
