from agents.common import SoundDesignPlan, run_structured_agent


async def sound_design_director_node(state):
    plan = await run_structured_agent(
        state,
        SoundDesignPlan,
        "Plan ambient audio, foley, and sound effects.",
        SoundDesignPlan(),
    )
    return {"sound_design": plan}
