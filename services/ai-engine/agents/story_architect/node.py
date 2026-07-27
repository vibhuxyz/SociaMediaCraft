from agents.common import StoryPlan, run_structured_agent, get_domain_knowledge
from workflow.registry import agent_registry

@agent_registry.register(
    "story_agent_node",
    runs_when=lambda state: "story" in state.get("director_plan", {}).get("capabilities", [])
)
async def story_agent_node(state):
    knowledge = get_domain_knowledge(state, ["storytelling", "advertising"])
    system_prompt = (
        "Create a scene-by-scene narrative structure with theme, conflict, and resolution.\n"
        "CRITICAL REQUIREMENTS:\n"
        "- You must strictly adhere to the duration specified in the director_plan.\n"
        "- The final scene MUST explicitly include the call to action (CTA) from the campaign_strategy.\n"
        + knowledge
    )

    plan = await run_structured_agent(
        state,
        StoryPlan,
        system_prompt,
        StoryPlan(), state_key="story"
    )
    return {"story": plan}
