from agents.common import AssetPlan
import time

async def asset_planner_node(state):
    start = time.perf_counter()
    
    prompt_pack = state.get("prompt_pack")
    
    total_images = 0
    total_videos = 0
    total_voice = 0
    total_music = 0
    total_sfx = 0
    
    # Safely parse scenes from the PromptEngineeringPlan
    scenes = []
    if prompt_pack:
        if hasattr(prompt_pack, "scenes"):
            scenes = prompt_pack.scenes
        elif isinstance(prompt_pack, dict):
            scenes = prompt_pack.get("scenes", [])
            
    for scene in scenes:
        shots = scene.shots if hasattr(scene, "shots") else scene.get("shots", [])
        for shot in shots:
            if hasattr(shot, "images"):
                total_images += len(shot.images)
            elif isinstance(shot, dict):
                total_images += len(shot.get("images", []))
                
            if hasattr(shot, "videos"):
                total_videos += len(shot.videos)
            elif isinstance(shot, dict):
                total_videos += len(shot.get("videos", []))
                
            if hasattr(shot, "voice"):
                if shot.voice: total_voice += 1
            elif isinstance(shot, dict):
                if shot.get("voice"): total_voice += 1
                
            if hasattr(shot, "music"):
                if shot.music: total_music += 1
            elif isinstance(shot, dict):
                if shot.get("music"): total_music += 1
                
            if hasattr(shot, "sfx"):
                total_sfx += len(shot.sfx)
            elif isinstance(shot, dict):
                total_sfx += len(shot.get("sfx", []))

    plan = AssetPlan(
        total_images_required=total_images,
        total_video_clips_required=total_videos,
        total_voice_tracks=total_voice,
        total_music_tracks=total_music,
        total_sfx=total_sfx,
        needs_thumbnail=True
    )
    
    end = time.perf_counter()
    print(f"[AI ENGINE] Execution Planner (Python Fast-Path) took {end-start:.4f}s")
    
    return {"asset_plan": plan}
