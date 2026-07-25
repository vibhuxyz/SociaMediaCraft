from agents.common import ShotPlan, run_structured_agent


async def shot_planner_node(state):
    plan = await run_structured_agent(
        state,
        ShotPlan,
        "Expand storyboard scenes into executable shots.",
        ShotPlan(),
    )
    return {"shot_plan": plan}
