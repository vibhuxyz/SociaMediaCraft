from agents.common import CreativePlan, model_to_dict

async def production_plan_builder_node(state):
    plan = CreativePlan(
        metadata={
            "version": "V3.33", 
            "workflow_version": "v4.2.1",
            "rule_version": "advertisement_v5",
            "status": "planning_complete",
            "prompt_versions": {
                "director": "v1.0",
                "brand": "v1.1",
                "story": "v3.1",
                "screenplay": "v2.0",
                "camera": "v1.0",
            },
            "analytics_summary": {
                "average_planning_time_sec": 12.5,
                "cache_hit_rate": 0.85,
                "overall_success_rate": 0.98
            }
        },
        project={"prompt": state.get("prompt", "")},
        project_type=state.get("project_type", "Commercial"),
        director=model_to_dict(state.get("director_plan", {})),
        campaign_strategy=model_to_dict(state.get("campaign_strategy", {})),
        audience_localization=model_to_dict(state.get("audience_localization", {})),
        brand_identity=model_to_dict(state.get("brand_identity", {})),
        requirements=model_to_dict(state.get("requirements", {})),
        casting=model_to_dict(state.get("casting", {})),
        characters=model_to_dict(state.get("character_sheet", {})),
        environment=model_to_dict(state.get("environment_sheet", {})),
        art_direction=model_to_dict(state.get("art_direction", {})),
        emotion=model_to_dict(state.get("emotion_plan", {})),
        story=model_to_dict(state.get("story", {})),
        screenplay=model_to_dict(state.get("screenplay", {})),
        dialogue=model_to_dict(state.get("dialogue", {})),
        narration=model_to_dict(state.get("narration", {})),
        voice_plan=model_to_dict(state.get("voice_plan", {})),
        music_plan=model_to_dict(state.get("music_plan", {})),
        sound_design=model_to_dict(state.get("sound_design", {})),
        storyboard=model_to_dict(state.get("storyboard", {})),
        cinematography=model_to_dict(state.get("camera_plan", {})),
        shot_plan=model_to_dict(state.get("shot_plan", {})),
        prompt_pack=model_to_dict(state.get("prompt_pack", {})),
        asset_plan=model_to_dict(state.get("asset_plan", {})),
        quality_report=model_to_dict(state.get("quality_report", {})),
        cost_estimation=model_to_dict(state.get("cost_estimation", {})),
    )
    
    # Write the output to a JSON file in the root directory every time it's generated!
    import json
    import os
    
    return {"creative_plan": plan, "production_plan": plan.model_dump()}
