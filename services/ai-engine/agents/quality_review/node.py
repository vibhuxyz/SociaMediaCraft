from agents.common import QualityReviewPlan, run_structured_agent


async def quality_review_node(state):
    required = ["director_plan", "story", "screenplay", "shot_plan", "asset_plan"]
    missing = [key for key in required if not state.get(key)]
    fallback = QualityReviewPlan(
        story_consistency_pass=not missing,
        character_consistency_pass=True,
        brand_consistency_pass=True,
        readiness_score=95 if not missing else 60,
        final_approval=not missing,
        feedback="Plan is ready for generation." if not missing else f"Missing required sections: {', '.join(missing)}",
    )
    plan = await run_structured_agent(
        state,
        QualityReviewPlan,
        "Validate story, character, brand, prompt, asset, and rendering readiness.",
        fallback,
    )
    return {"quality_report": plan}
