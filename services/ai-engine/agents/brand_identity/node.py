from agents.common import BrandIdentityPlan, run_structured_agent


async def brand_identity_node(state):
    plan = await run_structured_agent(
        state,
        BrandIdentityPlan,
        "Define brand personality, palette, typography, logo rules, and tagline.",
        BrandIdentityPlan(),
    )
    return {"brand_identity": plan}
