# Style Tokens Guide

Goal
Inject precise aesthetic "cheat codes" into prompts to instantly pull a specific visual style from the model's latent space.

High-Impact Tokens

1. **Film Stocks (For organic, cinematic looks):**
   - *Tokens:* "Kodak Portra 400" (warm, skin tones), "Cinestill 800T" (night, neon halation), "Fujifilm Superia" (cool greens/blues).

2. **Camera Brands (For specific sensor characteristics):**
   - *Tokens:* "ARRI Alexa 65" (premium Hollywood standard), "RED Monstro 8K" (ultra-sharp, high contrast), "iPhone 14 Pro" (UGC, sharp, deep depth of field).

3. **Directors/Cinematographers (Use with caution for copyright, better for mood boarding):**
   - *Tokens:* "Cinematography by Roger Deakins" (perfect lighting, silhouettes), "Directed by Wes Anderson" (symmetry, pastels), "Directed by Zack Snyder" (high contrast, slow motion, desaturated).

4. **Commercial Aesthetics:**
   - *Tokens:* "high-end editorial photography," "Vogue magazine cover," "Apple product photography aesthetic," "minimalist architectural digest."

How to Use
Do not stack too many conflicting style tokens. Combining "Kodak Portra" with "Cyberpunk 2077 aesthetic" will confuse the model. Pick ONE primary style anchor per shot.
