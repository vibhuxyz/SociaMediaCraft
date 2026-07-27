from agents.common import VoicePlan, run_structured_agent
from workflow.registry import agent_registry

@agent_registry.register(
    "voice_director_node",
    runs_when=lambda state: "voice" in state.get("director_plan", {}).get("capabilities", [])
)
async def voice_director_node(state):
    fallback = VoicePlan()
    plan = await run_structured_agent(
        state,
        VoicePlan,
        "You are the Voice Director. Decide ONLY if dialogue or narration or captions are needed, and list the speakers. Do NOT write the actual script.",
        fallback,
    )
    return {"voice_plan": plan.model_dump()}
