# Continuity Guide

Goal
Ensure seamless transitions between shots to maintain the illusion of continuous time and space.

Types of Continuity

1. **Temporal Continuity (Time):**
   - If Shot 1 happens at sunset, Shot 2 (five seconds later) cannot be in the pitch black of night. Lighting and shadows must remain consistent.

2. **Spatial Continuity (Space):**
   - The geography of the scene must make sense. If the door is on the left side of the room in the wide shot, the character must exit frame-left in the close-up.

3. **Action Continuity:**
   - Cutting on action. If a character raises their glass in a wide shot, the subsequent close-up must pick up the action seamlessly. (For AI, this is handled in the prompting by describing the exact state of the action).

4. **Prop/Wardrobe Continuity:**
   - The character cannot wear a jacket in Shot 1 and just a t-shirt in Shot 2 unless the action of taking it off is shown.

Handling AI Hallucinations
AI video generators are notoriously bad at continuity. To mitigate this:
- **Prompt strictly:** Always restate the core wardrobe, lighting, and environmental factors in every single prompt for a given scene.
- **Avoid complex interactions:** If a character must drink coffee, prompt the action of drinking, rather than prompting "holding a cup" and hoping the AI animates it to the mouth perfectly.
