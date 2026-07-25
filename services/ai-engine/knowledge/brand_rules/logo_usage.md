# Logo Usage Guide

Goal
Maintain strict visual integrity of the brand's primary identifier across all generated assets.

Core Principles
1. **Clear Space:** Always maintain a defined perimeter (padding) around the logo where no other visual elements, text, or complex backgrounds intrude.
2. **Minimum Size:** The logo must be legible on the smallest intended screen (e.g., mobile devices).
3. **Contrast:** The logo must stand out against the background. Use the appropriate color variant (e.g., full color, all-white, or all-black) depending on the scene's lighting.

Placement Rules
- **Intro/Outro:** Often centered on a clean background or superimposed over the final establishing shot.
- **Watermark (Bugs):** Placed in a corner (usually bottom right or top right) throughout the video, scaled down with partial transparency.
- **Product Integration:** If the logo is on the product itself, ensure the shot is composed so it is clearly visible and in focus at least once during the video.

Prompting Constraints for AI Generation
- **DO NOT** attempt to generate complex brand logos via image/video models (they will hallucinate text/shapes).
- **INSTEAD,** generate the scene with negative space and rely on the compositing/post-production pipeline to overlay the precise SVG/PNG logo asset.
- Specify "negative space in the bottom right corner" or "clean, uncluttered sky in the upper third" in prompts to leave room for the logo.

Avoid
- Placing the logo over busy or high-contrast textures.
- Stretching, squashing, or recoloring the logo outside of approved variants.
- Animating the logo with cheap effects (unless specifically requested by the brand).
