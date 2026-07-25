# Image Prompting Guide

Goal
Create high-fidelity, highly controllable still images (Midjourney, Stable Diffusion, DALL-E) that serve as the foundation for the video generation pipeline.

Core Structure of an Image Prompt
A professional prompt should follow this strict hierarchy:
1. **Medium / Format:** (e.g., "35mm film photograph", "cinematic still", "commercial photography")
2. **Subject & Action:** (e.g., "a woman in a red silk dress drinking espresso")
3. **Environment:** (e.g., "sitting in a sunlit Parisian cafe")
4. **Lighting:** (e.g., "soft morning light, golden hour, rim lighting")
5. **Camera & Lens:** (e.g., "shot on ARRI Alexa 65, 50mm lens, shallow depth of field")
6. **Color & Grading:** (e.g., "warm color palette, high contrast, Kodak Portra 400")
7. **Aspect Ratio/Parameters:** (e.g., "--ar 16:9 --style raw")

Rules for the Prompt Engineer
- Avoid abstract or subjective words ("beautiful," "amazing," "cool"). AI models do not understand subjectivity; they understand physics, lighting, and camera terminology.
- Use explicit visual descriptors. Instead of "sad lighting," use "low-key lighting, single softbox, deep crushed shadows."
