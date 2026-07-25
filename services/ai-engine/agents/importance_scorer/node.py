from agents.common import ImportanceScorerPlan, MissingFieldDecision, run_structured_agent


async def importance_scorer_node(state):
    ask_user_fields = {
        "brand rules",
        "call to action",
        "camera style",
        "coffee brand name",
        "coffee product type",
        "target audience",
        "unique selling proposition",
        "visual tone",
        "voice accent",
        "voiceover style",
    }
    decisions = [
        MissingFieldDecision(
            field=field,
            impact="High" if field in ask_user_fields else "Low",
            action="Ask user" if field in ask_user_fields else "Use defaults",
        )
        for field in dict.fromkeys(state.get("missing_information", []))
    ]
    plan = await run_structured_agent(
        state,
        ImportanceScorerPlan,
        "Decide which missing fields require user input and which can use defaults.",
        ImportanceScorerPlan(decisions=decisions),
    )
    critical = [decision.field for decision in plan.decisions if decision.action.lower() == "ask user"]
    return {"importance_scorer_plan": plan.model_dump(), "critical_missing_information": critical}
