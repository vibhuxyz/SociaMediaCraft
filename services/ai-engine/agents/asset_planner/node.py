from agents.common import AssetPlan, run_structured_agent


async def asset_planner_node(state):
    shot_plan = state.get("shot_plan")
    shot_count = len(getattr(shot_plan, "shots", []) or []) or 3
    fallback = AssetPlan(
        total_images_required=shot_count,
        total_video_clips_required=shot_count,
        total_voice_tracks=1,
        total_music_tracks=1,
        total_sfx=max(1, shot_count),
        needs_thumbnail=True,
    )
    plan = await run_structured_agent(
        state,
        AssetPlan,
        "Calculate exact asset counts required for generation and rendering.",
        fallback,
    )
    return {"asset_plan": plan}
