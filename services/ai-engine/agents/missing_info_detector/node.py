from agents.common import MissingInformationPlan, run_structured_agent


async def missing_info_detector_node(state):
    existing = list(
        dict.fromkeys(
            [
                *state.get("visual_missing_information", []),
                *state.get("audio_missing_information", []),
                *state.get("missing_information", []),
            ]
        )
    )
    fallback = MissingInformationPlan(missing_information=existing)
    plan = await run_structured_agent(
        state,
        MissingInformationPlan,
        "Compare available requirements against required creative information. Do NOT flag creative choices (e.g. camera, style, tone, mood, call to action) as missing. Only flag hard factual business requirements as missing. "
        "CRITICAL: Do NOT flag 'legal restrictions', 'brand guidelines (logos, colors)', or 'promotions/discounts' as missing unless the prompt explicitly implies they are needed. Assume they are not needed by default.",
        fallback,
    )
    return {"missing_information": plan.missing_information}
