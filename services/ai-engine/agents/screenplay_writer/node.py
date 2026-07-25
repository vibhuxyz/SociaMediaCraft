from agents.common import ScreenplayPlan, run_structured_agent


async def screenplay_writer_node(state):
    plan = await run_structured_agent(
        state,
        ScreenplayPlan,
        "Write professional scene-by-scene screenplay action lines.",
        ScreenplayPlan(),
    )
    return {"screenplay": plan}
