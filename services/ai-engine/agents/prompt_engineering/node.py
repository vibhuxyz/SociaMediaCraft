from agents.common import OptimizedPrompt, PromptEngineeringPlan, run_structured_agent


async def prompt_engineering_node(state):
    fallback = PromptEngineeringPlan(
        image_prompts=[
            OptimizedPrompt(target_engine="FLUX", prompt_text="cinematic keyframe, clean composition, production-ready detail")
        ],
        video_prompts=[
            OptimizedPrompt(target_engine="Veo", prompt_text="smooth cinematic motion, coherent subject, polished commercial pacing")
        ],
        audio_prompts=[
            OptimizedPrompt(target_engine="ElevenLabs", prompt_text="confident neutral delivery, medium pace, clear articulation")
        ],
    )
    plan = await run_structured_agent(
        state,
        PromptEngineeringPlan,
        "Convert the creative plan into optimized prompts for image, video, and audio providers.",
        fallback,
    )
    return {"prompt_pack": plan}
