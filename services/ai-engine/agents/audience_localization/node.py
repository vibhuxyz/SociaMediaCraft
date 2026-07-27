from agents.common import AudienceLocalizationPlan, run_structured_agent


async def audience_localization_node(state):
    plan = await run_structured_agent(
        state,
        AudienceLocalizationPlan,
        "Define country, language, accent, cultural context, and regional rules.",
        AudienceLocalizationPlan(), state_key="audience_localization"
    )
    return {"audience_localization": plan}
