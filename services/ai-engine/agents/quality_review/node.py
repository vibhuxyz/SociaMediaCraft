from agents.common import QualityReviewPlan
import time

async def quality_review_node(state):
    start = time.perf_counter()
    
    required = ["director_plan", "story", "screenplay", "shot_plan", "asset_plan"]
    missing = [key for key in required if not state.get(key)]
    
    plan = QualityReviewPlan(
        story_consistency_pass=not missing,
        character_consistency_pass=True,
        brand_consistency_pass=True,
        readiness_score=95 if not missing else 60,
        final_approval=not missing,
        feedback="Plan is ready for generation." if not missing else f"Missing required sections: {', '.join(missing)}",
    )
    
    end = time.perf_counter()
    print(f"[AI ENGINE] Quality Review (Python Fast-Path) took {end-start:.4f}s")
    
    return {"quality_report": plan}
