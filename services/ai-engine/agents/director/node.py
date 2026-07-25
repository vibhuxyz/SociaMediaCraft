import re

from agents.common import DirectorPlan, run_structured_agent


async def director_node(state):
    prompt = state.get("prompt", "")
    duration_match = re.search(r"(\d+\s*(?:s|sec|second|seconds|min|minute|minutes))", prompt, re.I)
    fallback = DirectorPlan(duration=duration_match.group(1) if duration_match else "60s")
    plan = await run_structured_agent(
        state,
        DirectorPlan,
        "Understand the user's creative vision and produce the director plan.",
        fallback,
    )
    return {"director_plan": plan.model_dump()}
