from agents.common import MotionPlan, run_structured_agent
from workflow.registry import agent_registry

@agent_registry.register(
    "motion_planner_node",
    runs_when=lambda state: "motion" in state.get("director_plan", {}).get("capabilities", [])
)
async def motion_planner_node(state):
    plan = await run_structured_agent(
        state,
        MotionPlan,
        "You are the Motion Planner. For every shot in the shot_plan, break down the 'action_description' into a highly precise chronological timeline of micro-actions. Example: 0.0-0.5s: look_at_cup, 0.5-1.2s: reach_right_hand, etc.",
        MotionPlan(),
        dependencies=["shot_plan"],
        state_key="motion_plan"
    )
    return {"motion_plan": plan}
