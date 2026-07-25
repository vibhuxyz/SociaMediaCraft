from agents.common import StoryPlan, run_structured_agent


async def story_agent_node(state):
    plan = await run_structured_agent(
        state,
        StoryPlan,
        "Create the narrative structure with beginning, middle, ending, conflict, and resolution.",
        StoryPlan(),
    )
    return {"story": plan}
