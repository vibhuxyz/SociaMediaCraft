from agents.common import ShotPlan, run_structured_agent

async def action_complexity_analyzer_node(state):
    plan = await run_structured_agent(
        state,
        ShotPlan,
        "Analyze the shots in the shot_plan. Assign a complexity_score (1-10) to each shot based on the actions happening. If complexity > 3, split the shot into multiple shorter shots (e.g. 4A, 4B, 4C) so each sub-shot only contains one major action.",
        state.get("shot_plan", ShotPlan()),
        dependencies=["shot_plan"],
        state_key="shot_plan"
    )
    return {"shot_plan": plan}
