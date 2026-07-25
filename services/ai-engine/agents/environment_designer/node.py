from agents.common import EnvironmentDesignPlan, run_structured_agent


async def environment_designer_node(state):
    plan = await run_structured_agent(
        state,
        EnvironmentDesignPlan,
        "Build the production locations, architecture, weather, lighting, and props.",
        EnvironmentDesignPlan(),
    )
    return {"environment_sheet": plan}
