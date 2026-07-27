from agents.common import KnownRequirement, RequirementAnalysisPlan, run_structured_agent


def _fallback_requirements(prompt: str, modality: str):
    lowered = prompt.lower()
    known = [KnownRequirement(name="modality", value=modality)]
    missing = []
    
    if "golden hour" in lowered:
        known.append(KnownRequirement(name="time_of_day", value="golden hour"))
    if "voice" in lowered or "narration" in lowered:
        known.append(KnownRequirement(name="voice", value="requested"))
    if "music" in lowered:
        known.append(KnownRequirement(name="music", value="requested"))
        
    if modality == "visual":
        if any(word in lowered for word in ["ad", "advert", "commercial"]):
            missing.extend(["brand name", "product name", "target audience"])
    
    return RequirementAnalysisPlan(known=known, missing=missing)


async def visual_analyzer_node(state):
    plan = await run_structured_agent(
        state,
        RequirementAnalysisPlan,
        "Extract known visual requirements and missing visual information. Do NOT flag creative choices (e.g. camera, style, tone) as missing.",
        _fallback_requirements(state.get("prompt", ""), "visual"),
    )
    return {"visual_requirements": plan.model_dump(), "visual_missing_information": plan.missing}


async def audio_analyzer_node(state):
    plan = await run_structured_agent(
        state,
        RequirementAnalysisPlan,
        "Extract known audio requirements and missing audio information. Do NOT flag creative choices (e.g. music mood, voice style) as missing.",
        _fallback_requirements(state.get("prompt", ""), "audio"),
    )
    return {"audio_requirements": plan.model_dump(), "audio_missing_information": plan.missing}
