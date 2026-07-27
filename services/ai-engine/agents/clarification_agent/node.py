from agents.common import ClarificationPlan, run_structured_agent


async def clarification_agent_node(state):
    missing_info = state.get("critical_missing_information", [])
    if not missing_info:
        return {"clarification_questions": [], "clarification_plan": {}}
        
    questions = [f"Please specify your preference for {field}." for field in missing_info]
    plan = await run_structured_agent(
        state,
        ClarificationPlan,
        "Generate concise dynamic questions for critical missing creative fields. "
        "CRITICAL INSTRUCTION: Do NOT ask the user to make creative decisions like camera angles, visual style, tone, mood, or call to action. "
        "Only ask for factual business constraints (e.g., Brand Name, Target Audience). "
        "CRITICAL: Do NEVER ask about 'legal restrictions/disclaimers', 'brand guidelines (logos, colors)', or 'promotions/discounts'. "
        "Do NOT ask for country or location, assume it is global unless provided. "
        "CRITICAL INSTRUCTION: You MUST ask a MAXIMUM of 2 questions total. Pick the 2 most critical missing fields.",
        ClarificationPlan(questions=questions),
    )
    
    # Deterministically enforce the 2 question limit and add the catch-all
    final_questions = plan.questions[:2]
    if len(final_questions) > 0:
        final_questions.append("Is there anything else you would like to mention?")
    plan.questions = final_questions
    
    return {"clarification_questions": plan.questions, "clarification_plan": plan.model_dump()}
