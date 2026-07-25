# Negative Prompting Guide

Goal
Ensure the AI avoids generating unwanted artifacts, hallucinations, or amateur aesthetics.

The Philosophy of the Negative Prompt
Negative prompts tell the AI what *not* to include. It is just as important as the positive prompt for maintaining a premium commercial look.

Essential Commercial Negative Tokens
- **For Humans:** "mutated hands, extra fingers, deformed face, crossed eyes, asymmetric eyes, unnatural skin texture, plastic skin, CGI, 3D render."
- **For Environments:** "clutter, messy background, text, watermarks, signatures, logos, messy composition, merged objects."
- **For Cinematic Quality:** "overexposed, underexposed, flat lighting, amateur photography, blurry, pixelated, low resolution, jpeg artifacts."

Application
- In tools like Stable Diffusion or Midjourney (using `--no`), append the relevant negative tokens to ensure a clean output.
- *Rule:* If the brand demands "Negative Space" for copy, the negative prompt MUST include: "clutter, background objects, busy background, distracting elements."
