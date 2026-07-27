from agents.common import ShotPlan, run_structured_agent

async def object_interaction_analyzer_node(state):
    plan = await run_structured_agent(
        state,
        ShotPlan,
        "Analyze each shot for risky object interactions (Human + Object + Touch, like drinking from a cup, opening a door). Identify these interactions and list them in risky_interactions. If highly risky, you may increase the complexity score or flag for a shorter duration.",
        state.get("shot_plan", ShotPlan()),
        dependencies=["shot_plan"],
        state_key="shot_plan"
    )
    return {"shot_plan": plan}
