from agents.common import BrandIdentityPlan, run_structured_agent
from workflow.registry import agent_registry

@agent_registry.register(
    "brand_identity_node",
    runs_when=lambda state: "branding" in state.get("director_plan", {}).get("capabilities", [])
)
async def brand_identity_node(state):
    plan = await run_structured_agent(
        state,
        BrandIdentityPlan,
        "Define brand personality, palette, typography, logo rules, and tagline.",
        BrandIdentityPlan(), state_key="brand_identity"
    )
    return {"brand_identity": plan}
