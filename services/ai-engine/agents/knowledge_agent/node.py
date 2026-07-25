from agents.common import KnowledgeResearchPlan, run_structured_agent


async def knowledge_agent_node(state):
    plan = await run_structured_agent(
        state,
        KnowledgeResearchPlan,
        "Summarize available brand knowledge, references, template rules, and localization context.",
        KnowledgeResearchPlan(),
    )
    return {"knowledge_research": plan}
