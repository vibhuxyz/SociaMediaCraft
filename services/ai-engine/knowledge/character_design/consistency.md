# Character Consistency Guide

Goal
Maintain the exact visual identity of a character across multiple shots, angles, and scenes.

The Consistency Problem in AI
Image and video generation models naturally want to create a slightly different person every time a new prompt is run. To fix this, we must anchor the character's core traits.

The "Character Bible" Prompting Technique
Create a dense, reusable string of tokens that defines the character's immutable traits. This string must be used in *every* prompt featuring this character.

Components of a Consistency String:
1. **Specific Name/Reference (Optional but helpful):** Using a blend of two celebrity names (e.g., "A mix of Idris Elba and Oscar Isaac") creates a unique, repeatable face latent.
2. **Detailed Facial Structure:** "High cheekbones, sharp jawline, straight nose, slight cleft chin."
3. **Specific Hair:** "Messy auburn hair parted on the left, slight stubble."
4. **Distinctive Features (Anchors):** Give the AI something specific to latch onto: "A small scar over the left eyebrow," "distinctive round tortoiseshell glasses," "freckles across the nose."
5. **Fixed Wardrobe:** Unless the story requires a change, keep them in a specific outfit: "Wearing a faded green bomber jacket over a white t-shirt."

Example Consistency Token String:
> "Portrait of [CHARACTER NAME], a 30-year-old woman with a sharp jawline, short curly black hair, wearing thick black rimmed glasses and a yellow raincoat."

Workflow for the Character Designer
- Step 1: Generate a "Character Sheet" (front, side, and 3/4 profiles) to lock in the look.
- Step 2: Extract the defining features into a standardized Prompt Block.
- Step 3: Pass this Prompt Block to the Prompt Engineer for every shot involving this character.
