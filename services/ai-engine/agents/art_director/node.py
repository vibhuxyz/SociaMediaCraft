from agents.common import ArtDirectionPlan, run_structured_agent, get_domain_knowledge


async def art_director_node(state):
    knowledge = get_domain_knowledge(state, ["visual_styles", "color_grading", "environments"])
    system_prompt = (
        "Create the visual language, lens, camera, film stock, grading, and mood.\n"
        + knowledge
    )

    plan = await run_structured_agent(
        state,
        ArtDirectionPlan,
        system_prompt,
        ArtDirectionPlan(), state_key="art_direction"
    )
    return {"art_direction": plan}
