from agents.common import CastingPlan, run_structured_agent


async def casting_director_node(state):
    plan = await run_structured_agent(
        state,
        CastingPlan,
        "Define roles, ages, archetypes, nationality, and build for all characters.",
        CastingPlan(),
    )
    return {"casting": plan}
