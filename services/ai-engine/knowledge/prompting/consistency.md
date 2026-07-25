# Character Consistency Guide

Goal
Ensure that the "hero" of the commercial looks like the exact same person across 15 different shots.

Theory
AI models naturally want to generate a new face every time. To maintain consistency, you must create a rigid "Character Bible" and inject it into every single prompt for that character.

The "Character Bible" Formula
You cannot just say "a handsome man." You must define their immutable physical traits.

*Example Character Token Block:*
`"A 35-year-old Japanese man, sharp jawline, short messy black hair, slight stubble, wearing a tailored navy blue turtleneck, distinct scar on left eyebrow."`

Rules for Consistency
1. **The Anchor Face:** In tools like Midjourney, use the Character Reference (`--cref`) parameter pointing to a master "anchor" image of the character's face.
2. **The Clothing:** Clothing *will* change unless explicitly prompted every time. The navy blue turtleneck must be mentioned in the wide shot, the medium shot, and the close-up.
3. **Avoid Props in Hands:** If a character is holding a coffee cup in shot 1, and shot 2 is a close-up of their face without the cup, do not mention the cup in shot 2, or the AI will try to awkwardly insert it near their face.
4. **Seed Numbers:** When possible, use the same generation Seed across multiple shots to retain the same underlying noise pattern.
