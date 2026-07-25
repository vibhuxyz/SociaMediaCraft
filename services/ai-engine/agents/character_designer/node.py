from agents.common import CharacterDesignPlan, run_structured_agent


async def character_designer_node(state):
    plan = await run_structured_agent(
        state,
        CharacterDesignPlan,
        "Create reusable visual character sheets.",
        CharacterDesignPlan(),
    )
    return {"character_sheet": plan}
