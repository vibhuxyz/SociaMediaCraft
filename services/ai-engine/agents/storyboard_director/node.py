from agents.common import StoryboardPlan, run_structured_agent


async def storyboard_director_node(state):
    plan = await run_structured_agent(
        state,
        StoryboardPlan,
        "Translate screenplay scenes into visual storyboard concepts.",
        StoryboardPlan(),
    )
    return {"storyboard": plan}
