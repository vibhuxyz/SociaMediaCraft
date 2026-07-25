from agents.common import DialoguePlan, run_structured_agent


async def dialogue_writer_node(state):
    plan = await run_structured_agent(
        state,
        DialoguePlan,
        "Write natural dialogue or explicitly decide the production has no dialogue.",
        DialoguePlan(),
    )
    return {"dialogue": plan}
