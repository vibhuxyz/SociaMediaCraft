from agents.common import MusicPlan, run_structured_agent


async def music_director_node(state):
    plan = await run_structured_agent(
        state,
        MusicPlan,
        "Plan musical score genre, tempo, mood, instruments, and ending build.",
        MusicPlan(),
    )
    return {"music_plan": plan}
