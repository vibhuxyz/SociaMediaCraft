from agents.common import NarrationPlan, run_structured_agent


async def narration_writer_node(state):
    plan = await run_structured_agent(
        state,
        NarrationPlan,
        "Create narration blocks with scene timing and tone indicators.",
        NarrationPlan(),
    )
    return {"narration": plan}
