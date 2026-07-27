from agents.common import ScreenplayPlan, run_structured_agent


async def screenplay_writer_node(state):
    plan = await run_structured_agent(
        state,
        ScreenplayPlan,
        "Write professional scene-by-scene screenplay action lines based exactly on the story plan scenes.",
        ScreenplayPlan(), state_key="screenplay",
        dependencies=["story"]
    )
    return {"screenplay": plan}
