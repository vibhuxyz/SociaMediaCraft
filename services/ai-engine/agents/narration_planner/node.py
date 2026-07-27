from agents.common import NarrationPlan, run_structured_agent
from workflow.registry import agent_registry

@agent_registry.register(
    "narration_planner_node",
    runs_when=lambda state: "narration" in state.get("director_plan", {}).get("capabilities", [])
)
async def narration_planner_node(state):
    fallback = NarrationPlan()
    plan = await run_structured_agent(
        state,
        NarrationPlan,
        "You are the Narration Planner. Write voiceover narration blocks for the scenes.",
        fallback,
    )
    return {"narration": plan.model_dump()}
