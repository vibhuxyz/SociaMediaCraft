from agents.common import ArtDirectionPlan, run_structured_agent


async def art_director_node(state):
    plan = await run_structured_agent(
        state,
        ArtDirectionPlan,
        "Create the visual language, lens, camera, film stock, grading, and mood.",
        ArtDirectionPlan(),
    )
    return {"art_direction": plan}
