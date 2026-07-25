from agents.common import EmotionPlan, run_structured_agent


async def emotion_analyzer_node(state):
    plan = await run_structured_agent(
        state,
        EmotionPlan,
        "Map emotional progression across the narrative.",
        EmotionPlan(),
    )
    return {"emotion_plan": plan}
