from agents.common import CampaignStrategy, run_structured_agent


async def commercial_agent_node(state):
    plan = await run_structured_agent(
        state,
        CampaignStrategy,
        "Define campaign goal, emotion, CTA, and core message.",
        CampaignStrategy(), state_key="campaign_strategy"
    )
    return {"campaign_strategy": plan}
