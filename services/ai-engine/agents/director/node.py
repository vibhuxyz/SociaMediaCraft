import re
from agents.common import DirectorPlan, run_structured_agent

async def director_node(state):
    prompt = state.get("prompt", "")
    duration_match = re.search(r"(\d+\s*(?:s|sec|second|seconds|min|minute|minutes))", prompt, re.I)
    
    # Sensible fallback
    fallback = DirectorPlan(
        project_type="advertisement",
        subtype="product_showcase",
        complexity="medium",
        style="modern",
        duration=duration_match.group(1) if duration_match else "30s",
        capabilities=["branding", "motion", "voice", "audio"]
    )
    
    system_prompt = """You are the Director Agent. Your ONLY job is to extract high-level metadata from the user's prompt. 
Determine the project_type (e.g. advertisement, cinematic_scene, short_film, product_showcase, talking_avatar), subtype, complexity (low, medium, high), style, and duration.
Also determine the 'capabilities' required. Output a list of strings such as:
- 'dialogue' (if spoken dialogue is needed)
- 'narration' (if a voiceover is needed)
- 'voice' (if any kind of voice/speech is needed)
- 'audio' (if music or sound effects are needed)
- 'motion' (if animation or camera movement is needed)
- 'branding' (if brand identity or logos are needed)
- 'story' (if a narrative is required)

Do NOT generate creative content or scripts, just return the structured plan."""

    plan = await run_structured_agent(
        state,
        DirectorPlan,
        system_prompt,
        fallback,
    )
    return {"director_plan": plan.model_dump()}
