async def cost_estimator_node(state):
    print("[AI ENGINE] Cost Estimator Agent running...")
    
    asset_plan = state.get("asset_plan", {})
    if hasattr(asset_plan, "model_dump"):
        asset_plan = asset_plan.model_dump()
        
    director_plan = state.get("director_plan", {})
    if hasattr(director_plan, "model_dump"):
        director_plan = director_plan.model_dump()

    images = asset_plan.get("total_images_required", 0)
    videos = asset_plan.get("total_video_clips_required", 0)
    voice_tracks = asset_plan.get("total_voice_tracks", 0)
    music_tracks = asset_plan.get("total_music_tracks", 0)
    duration_str = director_plan.get("duration", "30")
    
    try:
        duration_int = int(''.join(filter(str.isdigit, duration_str)))
    except ValueError:
        duration_int = 30

    # Pricing Assumptions
    # Flux: $0.03 per image
    # Veo: $3.00 per clip (assumed high quality)
    # ElevenLabs: $0.12 per track
    # Suno: $0.25 per track
    
    image_cost = images * 0.03
    video_cost = videos * 3.00
    voice_cost = voice_tracks * 0.12
    music_cost = music_tracks * 0.25
    storage_cost = 0.02
    
    total_cost = round(image_cost + video_cost + voice_cost + music_cost + storage_cost, 2)
    
    credits = {
        "images": images * 2,
        "videos": videos * 30,
        "voice": voice_tracks * 5,
        "music": music_tracks * 8,
    }
    credits["total"] = sum(credits.values())
    
    # Simple deterministic optimization checks
    can_reduce_cost = False
    suggestions = []
    
    if videos > 4:
        can_reduce_cost = True
        suggestions.append(f"Reduce video clips from {videos} to {max(4, videos - 2)} to save ${(videos - max(4, videos - 2)) * 3.00}")
    if images > 5:
        can_reduce_cost = True
        suggestions.append(f"Reuse character images to reduce generations")
        
    optimized_cost = total_cost
    if can_reduce_cost:
        optimized_cost = round(total_cost * 0.7, 2)
        
    from dependencies import planning_metrics
    
    cost_estimation = {
        "planning_metrics": {
            "total_time_sec": round(planning_metrics["total_time_sec"], 2),
            "total_cost_usd": round(planning_metrics["total_cost_usd"], 4),
            "api_calls": planning_metrics["api_calls"]
        },
        "estimated_cost": total_cost,
        "estimated_credits": credits["total"],
        "estimated_duration": f"{max(2, videos * 2)} min",
        "providers": {
            "image": "Flux Pro",
            "video": "Veo 3",
            "voice": "ElevenLabs",
            "music": "Suno"
        },
        "optimization": {
            "current_cost": total_cost,
            "optimized_cost": optimized_cost,
            "suggestions": suggestions
        },
        "optimization_score": 95 if not can_reduce_cost else 75,
        "can_reduce_cost": can_reduce_cost,
        "breakdown": {
            "image_generation": {"provider": "Flux Pro", "images": images, "cost": round(image_cost, 2)},
            "video_generation": {"provider": "Veo 3", "clips": videos, "cost": round(video_cost, 2)},
            "voice_generation": {"provider": "ElevenLabs", "cost": round(voice_cost, 2)},
            "music_generation": {"provider": "Suno", "cost": round(music_cost, 2)},
            "storage": storage_cost
        },
        "credits": credits
    }
    
    return {"cost_estimation": cost_estimation}
