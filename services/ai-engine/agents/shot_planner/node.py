from agents.common import ShotPlan, run_structured_agent


async def shot_planner_node(state):
    plan = await run_structured_agent(
        state,
        ShotPlan,
        "Expand storyboard scenes into executable shots.",
        ShotPlan(), state_key="shot_plan"
    )
    return {"shot_plan": plan}
