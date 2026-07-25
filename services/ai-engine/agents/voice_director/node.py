from agents.common import VoicePlan, run_structured_agent


async def voice_director_node(state):
    plan = await run_structured_agent(
        state,
        VoicePlan,
        "Plan voice provider, gender, accent, emotion, and pace.",
        VoicePlan(),
    )
    return {"voice_plan": plan}
