from agents.common import ClarificationPlan, run_structured_agent


async def clarification_agent_node(state):
    questions = [f"Please specify your preference for {field}." for field in state.get("critical_missing_information", [])]
    plan = await run_structured_agent(
        state,
        ClarificationPlan,
        "Generate concise dynamic questions for critical missing creative fields.",
        ClarificationPlan(questions=questions),
    )
    return {"clarification_questions": plan.questions, "clarification_plan": plan.model_dump()}
