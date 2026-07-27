from pydantic import BaseModel, Field
from typing import Literal

class ImageGenerationTask(BaseModel):
    model: str = "Flux"
    prompt: str
    negative_prompt: str = "blurry, watermark, low quality"
    width: int = 1920
    height: int = 1080
    cfg: float = 7.5
    steps: int = 30
    references: list[str] = Field(default_factory=list)
    seed: int = 1234

class VideoGenerationTask(BaseModel):
    model: str = "Veo"
    # "image": animate a keyframe generated in this shot's `images` list.
    # "text": generate video directly from the prompt, no keyframe image needed.
    source: Literal["image", "text"] = "image"
    prompt: str
    camera_motion: str = "Static"
    duration: int = 4

class VoiceGenerationTask(BaseModel):
    text: str
    voice: str
    emotion: str
    prompt: str

class MusicGenerationTask(BaseModel):
    genre: str
    mood: str
    duration: int
    prompt: str

class SfxCue(BaseModel):
    effect: str
    timestamp_offset: str

class PromptShot(BaseModel):
    shot_id: str
    duration: str
    camera: str
    transition: str
    images: list[ImageGenerationTask] = Field(default_factory=list)
    videos: list[VideoGenerationTask] = Field(default_factory=list)
    voice: VoiceGenerationTask | None = None
    music: MusicGenerationTask | None = None
    sfx: list[SfxCue] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)

class PromptScene(BaseModel):
    scene_id: int
    shots: list[PromptShot] = Field(default_factory=list)

class PromptEngineeringPlan(BaseModel):
    scenes: list[PromptScene] = Field(default_factory=list)
