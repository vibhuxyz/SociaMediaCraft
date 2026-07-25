from agents.brief_validator.schema import BriefValidationPlan
from agents.common import run_structured_agent


def _looks_like_missing_detail_error(error: str | None) -> bool:
    if not error:
        return False

    lowered = error.lower()
    missing_detail_phrases = [
        "lack",
        "lacks",
        "missing",
        "specific detail",
        "target audience",
        "key message",
        "unique selling proposition",
        "tone",
        "branding",
        "brand requirements",
        "not enough detail",
    ]
    return any(phrase in lowered for phrase in missing_detail_phrases)


def _looks_plannable_without_llm(prompt: str) -> bool:
    lowered = prompt.lower()
    creative_terms = [
        "ad",
        "advertisement",
        "commercial",
        "film",
        "reel",
        "video",
        "story",
        "promo",
        "product",
        "brand",
        "coffee",
        "coffe",
    ]
    return any(term in lowered for term in creative_terms)


async def brief_validator_node(state):
    prompt = (state.get("prompt") or "").strip()
    fallback = BriefValidationPlan(
        is_valid=bool(prompt) and _looks_plannable_without_llm(prompt),
        validation_error=None
        if prompt and _looks_plannable_without_llm(prompt)
        else "Prompt is required." if not prompt else "Prompt is not clear enough to plan a video.",
        warnings=[],
    )
    plan = await run_structured_agent(
        state,
        BriefValidationPlan,
        (
            "Validate whether the prompt can start a video planning workflow. "
            "Mark is_valid=false only when the prompt is empty, nonsensical, unrelated to video/creative production, "
            "unsafe, impossible to interpret, or impossible to plan at all. "
            "Do not reject sparse but understandable briefs. If the prompt is understandable but lacks target audience, "
            "brand, USP, tone, script, CTA, camera, or style details, set is_valid=true and put those gaps in warnings. "
            "Example valid sparse brief: 'create a coffee ad for 30 sec video'."
        ),
        fallback,
    )
    if prompt and not plan.is_valid and _looks_like_missing_detail_error(plan.validation_error):
        plan = BriefValidationPlan(
            is_valid=True,
            validation_error=None,
            warnings=[plan.validation_error or "Brief is sparse; missing details should be clarified downstream."],
        )
    return {
        "is_valid": plan.is_valid,
        "validation_error": plan.validation_error,
        "brief_validation": plan.model_dump(),
    }
