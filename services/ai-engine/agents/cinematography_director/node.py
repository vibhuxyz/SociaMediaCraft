from agents.common import CinematographyPlan, run_structured_agent, get_domain_knowledge


async def cinematography_director_node(state):
    knowledge = get_domain_knowledge(state, ["cinematography", "lenses", "lighting", "composition"])
    system_prompt = (
        "Define camera movement, lighting, composition, and depth of field.\n"
        + knowledge
    )

    plan = await run_structured_agent(
        state,
        CinematographyPlan,
        system_prompt,
        CinematographyPlan(), state_key="camera_plan"
    )
    return {"camera_plan": plan}
