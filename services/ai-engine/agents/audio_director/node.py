from agents.common import AudioPlan, run_structured_agent
from workflow.registry import agent_registry

@agent_registry.register(
    "audio_director_node",
    runs_when=lambda state: "audio" in state.get("director_plan", {}).get("capabilities", [])
)
async def audio_director_node(state):
    fallback = AudioPlan()
    plan = await run_structured_agent(
        state,
        AudioPlan,
        "You are the Audio Director. Plan the music selection, foley, ambient audio, sound effects, voice timing strategy, and audio mix strategy.",
        fallback,
    )
    return {"audio_plan": plan.model_dump()}
