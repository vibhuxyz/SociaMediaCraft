# Video Prompting Guide

Goal
Animate still images into highly realistic, physically accurate video clips (Sora, Runway Gen-2, Pika, Kling) while avoiding AI hallucinations and "morphing."

Core Concept: The Physics of Motion
Video AI models struggle with complex, multi-axis movement. Prompts must be explicitly constrained to simple physics.

Structuring the Video Prompt
1. **Camera Movement:** Start the prompt by explicitly defining the camera's physics. (e.g., "Slow horizontal tracking shot", "Static camera", "Subtle push in").
2. **Subject Movement:** Keep it simple and singular. (e.g., "the woman slowly turns her head to the left," "the steam rises gently from the coffee cup").
3. **Atmospheric Movement:** Add subtle motion to the environment to create depth. (e.g., "dust motes drifting in the light," "leaves rustling softly in the background").

Critical Constraints
- **NO Complex Physics:** Do not prompt for actions like "the man takes off his jacket, folds it, and puts it in his bag." The AI will morph his hands and the fabric into a Cronenberg monster. Stick to "the man smiles."
- **NO Text Generation in Video:** Do not prompt the video AI to generate text on a sign or a shirt. It will warp. All text/logos must be added in post-production.
- **Maintain Spatial Consistency:** The movement described must match the initial image (e.g., if the image is a close-up, do not prompt the camera to "zoom out to reveal the whole city").
