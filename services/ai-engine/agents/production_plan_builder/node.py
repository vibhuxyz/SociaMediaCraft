from agents.common import CreativePlan, model_to_dict


async def production_plan_builder_node(state):
    plan = CreativePlan(
        metadata={"version": "V3.33", "status": "planning_complete"},
        project={"prompt": state.get("prompt", "")},
        project_type=state.get("project_type", "Commercial"),
        director=model_to_dict(state.get("director_plan", {})),
        campaign_strategy=model_to_dict(state.get("campaign_strategy", {})),
        audience_localization=model_to_dict(state.get("audience_localization", {})),
        brand_identity=model_to_dict(state.get("brand_identity", {})),
        requirements={
            "visual": model_to_dict(state.get("visual_requirements", {})),
            "audio": model_to_dict(state.get("audio_requirements", {})),
            "missing": model_to_dict(state.get("missing_information", [])),
        },
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
    )
    return {"creative_plan": plan, "production_plan": plan.model_dump()}
