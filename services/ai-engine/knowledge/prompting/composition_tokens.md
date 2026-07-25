# Composition Tokens Guide

Goal
Force the AI to frame the subject exactly as the Cinematography Director planned, rather than letting the AI default to a centered medium shot.

Crucial Framing Tokens
- **Extreme Close Up (ECU):** "macro photography, extreme close up, filling the frame."
- **Close Up (CU):** "tight portrait, shoulders and head, 85mm lens."
- **Medium Shot (MS):** "medium shot, waist up, 50mm lens."
- **Wide Shot (WS):** "wide angle, full body shot, establishing shot, environmental context."
- **Extreme Wide Shot (EWS):** "extreme wide shot, massive scale, tiny subject in vast landscape, aerial view."

Crucial Placement Tokens
- "Subject placed on the far left third of the frame."
- "Rule of thirds composition."
- "Perfectly symmetrical center framing."
- "Negative space on the right side of the image."
- "Low angle, looking up at the subject (heroic)."
- "High angle, looking down at the subject (vulnerable)."

Troubleshooting
If the AI ignores the composition tokens, increase the *weight* of those specific words (e.g., in Midjourney, `extreme wide shot::2`).
