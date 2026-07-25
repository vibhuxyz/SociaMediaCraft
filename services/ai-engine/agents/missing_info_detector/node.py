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
        "Compare available requirements against required creative information.",
        fallback,
    )
    return {"missing_information": plan.missing_information}
