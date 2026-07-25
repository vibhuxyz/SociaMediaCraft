from agents.common import CinematographyPlan, run_structured_agent


async def cinematography_director_node(state):
    plan = await run_structured_agent(
        state,
        CinematographyPlan,
        "Define camera movement, lighting, composition, and depth of field.",
        CinematographyPlan(),
    )
    return {"camera_plan": plan}
