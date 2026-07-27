from agents.common import DialoguePlan, run_structured_agent
from workflow.registry import agent_registry

@agent_registry.register(
    "dialogue_planner_node",
    runs_when=lambda state: "dialogue" in state.get("director_plan", {}).get("capabilities", [])
)
async def dialogue_planner_node(state):
    fallback = DialoguePlan()
    plan = await run_structured_agent(
        state,
        DialoguePlan,
        "You are the Dialogue Planner. Write spoken dialogue lines for the characters specified by the Voice Director.",
        fallback,
    )
    return {"dialogue": plan.model_dump()}
