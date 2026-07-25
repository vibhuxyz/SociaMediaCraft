from agents.classifier.schema import ClassifierPlan
from agents.common import infer_project_type, run_structured_agent


async def classifier_node(state):
    fallback = ClassifierPlan(project_type=infer_project_type(state.get("prompt", "")))
    plan = await run_structured_agent(
        state,
        ClassifierPlan,
        "Classify the project type for the planning workflow.",
        fallback,
    )
    return {"project_type": plan.project_type, "classifier_plan": plan.model_dump()}
