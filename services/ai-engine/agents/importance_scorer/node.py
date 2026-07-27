from agents.common import ImportanceScorerPlan, MissingFieldDecision, run_structured_agent


async def importance_scorer_node(state):
    # Only ask the user for hard factual information that the AI cannot invent safely.
    # We should NOT ask for creative decisions (like camera, tone, style, CTA) because 
    # the AI is responsible for generating those using the loaded Knowledge Base and Templates.
    factual_fields = {
        "brand name",
        "product name",
        "unique selling proposition",
        "target audience",
    }
    
    decisions = [
        MissingFieldDecision(
            field=field,
            impact="High" if any(f in field.lower() for f in factual_fields) else "Low",
            action="Ask user" if any(f in field.lower() for f in factual_fields) else "Use AI defaults",
        )
        for field in dict.fromkeys(state.get("missing_information", []))
    ]
    
    system_prompt = (
        "Decide which missing fields require user input and which can use defaults.\n"
        "CRITICAL INSTRUCTION: You are an autonomous AI Video Engine. Do NOT ask the user for creative choices "
        "(e.g., camera angles, visual style, tone, mood, call to action, voiceover style). "
        "You must ONLY ask for strictly factual business requirements (e.g., Brand Name, Product Name)."
    )
    
    plan = await run_structured_agent(
        state,
        ImportanceScorerPlan,
        system_prompt,
        ImportanceScorerPlan(decisions=decisions),
    )
    
    critical = [decision.field for decision in plan.decisions if "ask user" in decision.action.lower()]
    return {"importance_scorer_plan": plan.model_dump(), "critical_missing_information": critical}
