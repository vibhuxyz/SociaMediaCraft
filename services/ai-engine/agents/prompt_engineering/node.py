from .schema import PromptEngineeringPlan
from agents.common import run_structured_agent, get_domain_knowledge
from litellm import acompletion
import json
import time

async def prompt_engineering_node(state):
    start = time.perf_counter()
    
    knowledge = get_domain_knowledge(state, ["prompting", "presets", "voice"])
    
    system_prompt_generator = (
        "You are the Lead Prompt Engineering Committee. Review the creative constraints, including the highly detailed motion_plan.\n"
        "RULES:\n"
        "1. DO NOT pad prompts with excessive adjectives. Be precise and structured.\n"
        "2. Structure every IMAGE and VIDEO prompt exactly like this:\n"
        "   Subject: [Details]\n"
        "   Environment: [Details]\n"
        "   Camera: [Details]\n"
        "   Lighting: [Details]\n"
        "   Motion Sequence: [From motion_plan, verbatim step-by-step list]\n"
        "   Facial Expression: [Details]\n"
        "   Object Interaction: [Details]\n"
        "   Negative Constraints: [What to avoid]\n"
        "3. Copy exact Art Direction & Brand Identity values.\n"
        "4. Generate VideoGenerationTask for EVERY shot.\n"
        "5. Populate 'references' with exact string paths.\n"
        "6. Explicitly populate 'depends_on' (e.g. '1.1_image').\n"
        "7. VOICE: 'VOICE DIRECTION: [Provider]. Deliver line \"[text]\" with [Emotion], [Pace].'\n"
        "8. MUSIC: 'MUSIC BRIEF: [Genre], [Tempo], [Instrumentation].'\n"
        "9. SFX: timed cue sheet.\n"
        "10. IMAGE-VIDEO PAIRING: set VideoGenerationTask.source to exactly 'image' or 'text' — no other value.\n"
        "    Default to 'image': generate a matching ImageGenerationTask in this shot as the keyframe to animate.\n"
        "    Only use 'text' (skip the image entirely) when the shot is a pure camera move/establishing/environment\n"
        "    shot with no single frozen moment worth using as a keyframe.\n"
        "11. IMAGE STYLE TAGS: after the structured block, every ImageGenerationTask.prompt must end with a single\n"
        "    'Style Tags:' line listing comma-separated quality/style modifiers appropriate to the shot\n"
        "    (e.g. Photorealistic, Cinematic lighting, Ultra detailed, 8K, Shallow depth of field, plus the specific\n"
        "    lens/angle already established for the shot). Do not add these tags to VIDEO prompts — video models\n"
        "    need the motion sequence, not style keyword stacking.\n"
        + knowledge
    )

    critic_prompt = (
        "You are the Prompt Critic. You are aggressively strict.\n"
        "Review the generated PromptEngineeringPlan.\n"
        "CRITICAL RULES YOU MUST ENFORCE:\n"
        "1. Structure: Every single image and video prompt MUST be structured with headers (Subject, Environment, Camera, Lighting, Motion Sequence, etc). Reject paragraphs of text.\n"
        "2. Motion: The Motion Sequence must be a clear step-by-step chronological list derived from the motion_plan. If it describes motion as a generic paragraph, REJECT it.\n"
        "3. Lip-Sync: Video prompts must contain explicit lip-sync facial expression instructions.\n"
        "4. Source: Every VideoGenerationTask.source must be exactly 'image' or 'text'. If it's any other value, REJECT it.\n"
        "5. Style Tags: Every ImageGenerationTask.prompt MUST end with a 'Style Tags:' line of comma-separated quality/style modifiers. Video prompts must NOT have a Style Tags line. REJECT if either is violated.\n"
        "If PERFECT, output exactly: 'APPROVED'.\n"
        "If FLAWED, output exactly what needs to be fixed. Do not hold back."
    )

    # 3. CRITIC & REFINE LOOP
    max_retries = 2
    attempt = 0
    plan = None
    
    while attempt <= max_retries:
        # Generate
        plan = await run_structured_agent(
            state,
            PromptEngineeringPlan,
            system_prompt_generator,
            PromptEngineeringPlan() if plan is None else plan, # Pass previous plan as baseline if retrying
            dependencies=["shot_plan", "motion_plan", "art_direction", "voice_plan", "music_plan", "sound_design", "environment_sheet", "character_sheet"],
            state_key="prompt_pack"
        )

        # Critic
        critic_response = await acompletion(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": critic_prompt},
                {"role": "user", "content": f"Review this plan: {plan.model_dump_json()}"}
            ],
            temperature=0.0
        )
        
        feedback = critic_response.choices[0].message.content.strip()
        if "APPROVED" in feedback.upper():
            break
        else:
            # Inject feedback into the generator for the next loop
            system_prompt_generator += f"\n\nCRITIC FEEDBACK FROM LAST ATTEMPT. FIX THESE: {feedback}"
            attempt += 1

    end = time.perf_counter()
    
    # Print the final prompt_pack as requested
    if plan:
        print("\n=== FINAL GENERATED PROMPT PACK ===")
        print(json.dumps(plan.model_dump(), indent=2))
        print("===================================\n")
    
    return {"prompt_pack": plan}
