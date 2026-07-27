import json
from typing import Any, Dict

def build_image_context(creative_plan: Dict[str, Any]) -> list[Dict[str, Any]]:
    """
    Builds the isolated context needed by the Image Generation Model
    for each timeline event in the execution plan.
    """
    
    # 1. Extract the shared context
    story = creative_plan.get("story", {})
    screenplay = creative_plan.get("screenplay", {})
    art_direction = creative_plan.get("art_direction", {})
    environment = creative_plan.get("environment", {})
    characters = creative_plan.get("characters", {})
    brand_identity = creative_plan.get("brand_identity", {})
    emotion = creative_plan.get("emotion", {})
    
    # 2. Extract Execution Plan
    asset_plan = creative_plan.get("asset_plan", {})
    execution_plan = asset_plan.get("execution_plan", {})
    if not execution_plan:
        return []
        
    scenes = execution_plan.get("scenes", [])
    
    image_contexts = []
    
    for scene in scenes:
        scene_id = scene.get("scene_id")
        timeline = scene.get("timeline", [])
        
        # Find relevant scene from story/screenplay
        story_scene = next((s for s in story.get("scenes", []) if s.get("scene_number") == scene_id), {})
        screenplay_scene = next((s for s in screenplay.get("scenes", []) if s.get("scene_number") == scene_id), {})
        
        for idx, event in enumerate(timeline):
            image_id = event.get("image")
            
            # Build the isolated context
            context = {
                "scene": scene_id,
                "image_id": image_id,
                "start_time": event.get("start"),
                "end_time": event.get("end"),
                "animation": event.get("animation"),
                "story_context": story_scene.get("action", ""),
                "screenplay_context": screenplay_scene.get("action_lines", ""),
                "art_style": art_direction.get("visual_style", ""),
                "lighting": art_direction.get("lighting_style", ""),
                "camera": art_direction.get("camera_movement", ""),
                "mood": emotion.get("primary_emotion", ""),
                "environment": environment.get("locations", [{}])[0].get("name", "Unknown"),
                "aspect_ratio": art_direction.get("aspect_ratio", "16:9"),
                "resolution": "1920x1080",
                "negative_prompt": "blurry, low quality, duplicate hands, distorted faces, bad anatomy"
            }
            image_contexts.append(context)
            
    return image_contexts


def build_video_context(creative_plan: Dict[str, Any], image_contexts: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
    """Builds isolated context for Video Generation Models (Veo, Runway, Pika)."""
    video_contexts = []
    
    for img_ctx in image_contexts:
        # A video model needs the generated image, the prompt, camera motion, and duration.
        dur = img_ctx.get("end_time", 5.0) - img_ctx.get("start_time", 0.0)
        
        ctx = {
            "reference_image": f"{img_ctx.get('image_id')}.png",
            "prompt": img_ctx.get("story_context") + " " + img_ctx.get("screenplay_context"),
            "camera_motion": img_ctx.get("animation", {}).get("camera", "static"),
            "duration": dur,
            "fps": 24,
            "aspect_ratio": img_ctx.get("aspect_ratio", "16:9")
        }
        video_contexts.append(ctx)
        
    return video_contexts


def build_voice_context(creative_plan: Dict[str, Any]) -> list[Dict[str, Any]]:
    """Builds isolated context for TTS Models (ElevenLabs, PlayHT)."""
    voice_plan = creative_plan.get("voice_plan", {})
    narration_plan = creative_plan.get("narration", {})
    dialogue_plan = creative_plan.get("dialogue", {})
    
    voice_contexts = []
    
    # Process Narration Blocks
    if narration_plan.get("has_narration", True):
        for block in narration_plan.get("blocks", []):
            ctx = {
                "text": block.get("text", ""),
                "voice": f"{voice_plan.get('gender', 'Neutral')} {voice_plan.get('accent', 'Neutral')}",
                "emotion": block.get("tone_indicator", voice_plan.get("emotion", "Friendly")),
                "speed": 1.0,
                "language": creative_plan.get("audience_localization", {}).get("language", "English")
            }
            voice_contexts.append(ctx)
            
    # Process Dialogue Blocks
    if dialogue_plan.get("has_dialogue", False):
        for line in dialogue_plan.get("lines", []):
            ctx = {
                "text": line.get("text", ""),
                "voice": f"{line.get('character_name', 'Actor')} Default",
                "emotion": line.get("emotion", "Neutral"),
                "speed": 1.0,
                "language": creative_plan.get("audience_localization", {}).get("language", "English")
            }
            voice_contexts.append(ctx)
            
    return voice_contexts


def build_music_context(creative_plan: Dict[str, Any]) -> Dict[str, Any]:
    """Builds isolated context for Music Generation Models (Suno, Udio, Asset Library)."""
    music_plan = creative_plan.get("music_plan", {})
    director_plan = creative_plan.get("director", {})
    
    dur_str = director_plan.get("duration", "30s").replace("s", "")
    try:
        duration_sec = int(dur_str)
    except:
        duration_sec = 30
        
    return {
        "genre": music_plan.get("genre", "Cinematic"),
        "mood": music_plan.get("mood", "Warm"),
        "energy": music_plan.get("tempo", "Medium"),
        "duration": duration_sec
    }


def build_sfx_context(creative_plan: Dict[str, Any]) -> list[Dict[str, Any]]:
    """Builds isolated context for SFX Models (ElevenLabs SFX, AudioLDM, or Asset Library)."""
    sound_design = creative_plan.get("sound_design", {})
    sfx_contexts = []
    
    # Process Ambient
    for ambient in sound_design.get("ambient", []):
        sfx_contexts.append({
            "effect": ambient,
            "duration": 5,
            "search": ambient.split(" ")[-1]
        })
        
    # Process SFX
    for sfx in sound_design.get("sfx", []):
        sfx_contexts.append({
            "effect": sfx,
            "duration": 2,
            "search": sfx.split(" ")[-1]
        })
        
    return sfx_contexts


def build_lipsync_context(video_filename: str, audio_filename: str) -> Dict[str, Any]:
    """Builds isolated context for Lip Sync Models (SyncLabs, Wav2Lip)."""
    return {
        "video": video_filename,
        "audio": audio_filename
    }


if __name__ == "__main__":
    print("Execution Context Builders loaded for: Image, Video, Voice, Music, SFX, LipSync.")
