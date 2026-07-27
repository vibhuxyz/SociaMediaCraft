"""
Prompt Optimizer
================
A post-processing layer that sits between the Prompt Builder's raw assembly
and the provider adapter.  It transforms a flat string into a rich,
structured, de-duplicated, fully-enriched generation prompt.

Pipeline (all steps run in order):
  1. Deduplication       — remove repeated concepts, keep the strongest form
  2. CharacterEnricher   — expand sparse character refs into full visual profiles
  3. EnvironmentEnricher — expand location names into prop/atmosphere inventories
  4. ActionEnricher      — unpack verbs into micro-action sequences
  5. CameraEnricher      — expand shot types into full cinematography specs
  6. LightingEnricher    — expand lighting cues into volumetric descriptors
  7. StylePreset         — inject commercial photography presets
  8. CompositionEnricher — add composition rules (rule-of-thirds, leading lines…)
  9. EmotionalIntent     — add viewer-experience directive
 10. NegativePrompt      — return provider-specific negative prompt library

Each enricher is a pure function (dict | str → str).  They have no side
effects and do not call any external service — all logic is deterministic
so the whole optimizer is synchronous and adds ~0 latency.
"""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger("ai-engine.prompt_optimizer")


# ═══════════════════════════════════════════════════════════════════════════
# 1. Deduplication
# ═══════════════════════════════════════════════════════════════════════════

# Concept groups: if multiple synonyms are found, keep only the strongest.
# Ordered strongest → weakest within each group.
_CONCEPT_GROUPS: list[list[str]] = [
    ["golden hour", "golden morning sunlight", "warm amber", "warm highlights",
     "warm light", "warm lighting", "warm atmosphere", "warm tone",
     "warm color grading", "warm"],
    ["cinematic", "film-like", "movie quality"],
    ["photorealistic", "photo-realistic", "hyper-realistic", "realistic"],
    ["ultra detailed", "highly detailed", "high detail", "detailed"],
    ["8k", "4k", "high resolution", "high-resolution"],
    ["soft bokeh", "bokeh", "shallow depth of field", "soft dof", "dof"],
    ["natural light", "natural lighting", "sunlight"],
    ["dramatic shadows", "deep shadows", "strong shadows", "shadows"],
]

def _deduplicate(text: str) -> str:
    """Remove repeated concept synonyms; keep the strongest representative."""
    lower = text.lower()
    suppressed: set[str] = set()

    for group in _CONCEPT_GROUPS:
        found = [term for term in group if term in lower]
        if len(found) <= 1:
            continue
        # Keep the first (strongest) term; mark the rest for removal.
        for duplicate in found[1:]:
            suppressed.add(duplicate)

    if not suppressed:
        return text

    result = text
    for term in sorted(suppressed, key=len, reverse=True):   # longest first to avoid partial matches
        # Word-boundary-aware removal (case-insensitive)
        result = re.sub(
            r"(?i)\b" + re.escape(term) + r"\b[,.]?\s*",
            "",
            result,
        )

    # Collapse multiple punctuation/spaces left behind
    result = re.sub(r"[ ,]{2,}", ", ", result)
    result = re.sub(r",\s*\.", ".", result)
    result = result.strip(" ,.")

    removed_count = len(suppressed)
    logger.debug(f"[Dedup] Removed {removed_count} duplicate concept(s)")
    return result


# ═══════════════════════════════════════════════════════════════════════════
# 2. Character Enricher
# ═══════════════════════════════════════════════════════════════════════════

# Archetype → default visual profile.  The resolver fills gaps; the AI plan
# overrides anything it explicitly specifies.
_CHARACTER_ARCHETYPES: dict[str, dict[str, str]] = {
    "barista": {
        "age": "mid-20s", "expression": "friendly, focused smile",
        "face": "oval face, natural makeup", "eyes": "warm brown eyes",
        "skin": "medium skin tone", "build": "slim, average height",
        "outfit_default": "black apron over white shirt, rolled sleeves",
    },
    "chef": {
        "age": "30s", "expression": "focused, confident",
        "face": "strong jawline, clean-shaven", "eyes": "dark eyes",
        "skin": "olive skin tone", "build": "athletic build",
        "outfit_default": "white chef's coat, kitchen towel at waist",
    },
    "model": {
        "age": "early 20s", "expression": "composed, aspirational",
        "face": "high cheekbones, defined features", "eyes": "striking eyes",
        "skin": "radiant skin tone", "build": "tall, slender",
        "outfit_default": "elegant, editorial attire",
    },
    "customer": {
        "age": "late 20s", "expression": "relaxed, content",
        "face": "approachable features, light smile", "eyes": "bright eyes",
        "skin": "fair skin tone", "build": "average build",
        "outfit_default": "smart casual — fitted jeans, simple top",
    },
}

def _enrich_character(character: dict | None, base_prompt: str) -> str:
    """Return a rich character description string.

    Uses the character sheet from the ProjectContext if available, then fills
    any blanks from the archetype table, inferred from the character's name or
    the base_prompt keywords.
    """
    if not character:
        return ""

    name  = character.get("name", "").lower()
    app   = character.get("appearance", {})
    outfits = character.get("outfits", [])

    # Infer archetype from name or base prompt
    archetype: dict = {}
    for key in _CHARACTER_ARCHETYPES:
        if key in name or key in base_prompt.lower():
            archetype = _CHARACTER_ARCHETYPES[key]
            break

    age        = app.get("age")        or archetype.get("age", "")
    expression = app.get("expression") or archetype.get("expression", "natural expression")
    face       = app.get("face")       or archetype.get("face", "")
    eyes       = app.get("eyes")       or archetype.get("eyes", "")
    skin       = app.get("skin")       or archetype.get("skin", "")
    build      = app.get("build")      or archetype.get("build", "")

    outfit = ""
    if outfits:
        outfit = outfits[0] if isinstance(outfits[0], str) else outfits[0].get("description", "")
    if not outfit:
        outfit = archetype.get("outfit_default", "")

    char_name = character.get("name", "Person")
    parts = [f"{char_name}"]
    if age:        parts.append(age)
    if build:      parts.append(build)
    if skin:       parts.append(f"{skin} skin")
    if face:       parts.append(face)
    if eyes:       parts.append(eyes)
    if expression: parts.append(expression)
    if outfit:     parts.append(f"wearing {outfit}")

    return ", ".join(filter(None, parts))


# ═══════════════════════════════════════════════════════════════════════════
# 3. Environment Enricher
# ═══════════════════════════════════════════════════════════════════════════

_ENV_PROPS: dict[str, list[str]] = {
    "coffee shop": [
        "large floor-to-ceiling windows", "reclaimed oak communal tables",
        "La Marzocca espresso machine", "hand-operated coffee grinder",
        "trailing pothos and fiddle-leaf fig plants", "exposed brick feature wall",
        "hand-written menu board", "ceramic artisan mugs on open shelving",
        "Edison-bulb pendant lights", "leather bar stools",
    ],
    "café": [
        "marble-top café tables", "wicker bistro chairs",
        "chalkboard specials board", "glass pastry display case",
        "fresh flower arrangements", "vintage coffee posters",
    ],
    "kitchen": [
        "stainless steel prep surfaces", "open shelving with mise-en-place bowls",
        "overhead extraction hood", "cast-iron skillets on pot rack",
        "fresh herbs in terracotta pots", "knife magnetic strip on tile wall",
    ],
    "living room": [
        "modular linen sofa", "low-profile oak coffee table",
        "floor lamp casting warm cone of light", "gallery wall of framed art",
        "woven area rug", "bookshelf styled with objects",
    ],
    "outdoor": [
        "dappled natural sunlight through tree canopy",
        "cobblestone pavement", "street planters with seasonal blooms",
        "distant architectural backdrop", "natural ambient sound implied",
    ],
    "studio": [
        "seamless paper backdrop", "professional softbox lighting rigs",
        "minimalist clean floor", "reflector panels", "lens flare from key light",
    ],
}

def _enrich_environment(environment: dict | None) -> str:
    """Return a rich environment description including props and atmosphere."""
    if not environment:
        return ""

    name     = environment.get("name", "")
    arch     = environment.get("architecture", "")
    lighting = environment.get("lighting", "")
    tod      = environment.get("time_of_day", "")
    weather  = environment.get("weather", "")
    props    = environment.get("props", [])

    # Look up canonical prop list
    canonical_props: list[str] = []
    name_lower = name.lower()
    for key, prop_list in _ENV_PROPS.items():
        if key in name_lower:
            canonical_props = prop_list[:6]   # top 6 to keep prompt focused
            break

    # Merge with any props from the plan (plan's explicit props take priority)
    all_props = list(props) + [p for p in canonical_props if p not in props]

    parts: list[str] = [name]
    if arch:    parts.append(arch)
    if tod:     parts.append(f"{tod} light")
    if weather: parts.append(weather)
    if lighting and "warm" not in lighting.lower():  # avoid dup with lighting enricher
        parts.append(lighting)
    if all_props:
        parts.append("featuring " + ", ".join(all_props[:5]))

    return ", ".join(filter(None, parts))


# ═══════════════════════════════════════════════════════════════════════════
# 4. Action Enricher
# ═══════════════════════════════════════════════════════════════════════════

# Key verb → ordered micro-action sequence
_ACTION_EXPANSIONS: dict[str, list[str]] = {
    "pour":    ["tilts pitcher at precise 45°", "thin stream of steamed milk spirals in",
                "heart latte art forms on surface", "cup placed gently on saucer",
                "client's face softens into smile"],
    "make":    ["selects finest beans with deliberate hand", "grinds to coarse-medium consistency",
                "tamps evenly with calibrated pressure", "espresso flows amber-gold",
                "steam wand froths milk to silky microfoam"],
    "prepare": ["measures ingredients with precision", "assembles components in sequence",
                "checks presentation from multiple angles", "final garnish placed",
                "dish slides forward on wooden board"],
    "serve":   ["approaches with quiet confidence", "sets item down without a sound",
                "brief warm eye contact and slight nod", "steps back to give space"],
    "smile":   ["genuine smile reaches the eyes", "slight head tilt",
                "warmth radiates to viewer", "moment of authentic human connection"],
    "walk":    ["purposeful stride", "shoulders relaxed", "natural arm swing",
                "environment reacts — slight stir in background"],
    "taste":   ["spoon or cup raised slowly", "first contact — eyes close briefly",
                "texture and flavour register on face", "satisfied exhale"],
}

def _enrich_action(base_prompt: str) -> str:
    """Expand action verbs in the base prompt into micro-action sequences."""
    result = base_prompt
    for verb, sequence in _ACTION_EXPANSIONS.items():
        if verb in base_prompt.lower():
            expanded = "; ".join(sequence)
            result = re.sub(
                rf"(?i)\b{verb}s?\b",
                f"[{expanded}]",
                result,
                count=1,
            )
            break   # one expansion per prompt keeps it readable
    return result


# ═══════════════════════════════════════════════════════════════════════════
# 5. Camera Enricher
# ═══════════════════════════════════════════════════════════════════════════

_CAMERA_PRESETS: dict[str, dict[str, str]] = {
    "wide": {
        "angle": "eye-level wide shot",
        "lens":  "24mm prime",
        "comp":  "rule of thirds, foreground elements frame subject, background establishes space",
        "depth": "natural depth, mid-range bokeh",
    },
    "close": {
        "angle": "intimate close-up",
        "lens":  "85mm portrait prime",
        "comp":  "subject fills 60% of frame, negative space intentional",
        "depth": "razor-thin depth of field, background melts away",
    },
    "medium": {
        "angle": "three-quarter medium shot",
        "lens":  "50mm standard prime",
        "comp":  "subject centred, breathing room left and right",
        "depth": "balanced depth, context visible",
    },
    "overhead": {
        "angle": "90° overhead flat-lay",
        "lens":  "35mm",
        "comp":  "symmetrical arrangement, intentional negative space, tactile textures prominent",
        "depth": "pan-focus, everything sharp",
    },
    "establishing": {
        "angle": "low-angle wide establishing shot",
        "lens":  "16mm",
        "comp":  "leading lines draw eye to subject, environment context dominant",
        "depth": "deep focus, foreground to infinity sharp",
    },
}

def _enrich_camera(art: dict | None, generation: dict | None) -> str:
    """Return a cinematography description from shot type and art direction."""
    shot_type     = (generation or {}).get("shot_type", "")
    camera_motion = (generation or {}).get("camera_motion", "")
    lens          = (art or {}).get("lens", "")

    # Find best preset
    preset: dict = {}
    for key, p in _CAMERA_PRESETS.items():
        if key in (shot_type or "").lower():
            preset = p
            break
    if not preset:
        preset = _CAMERA_PRESETS["medium"]   # sensible default

    parts = [
        preset.get("angle", ""),
        f"{lens or preset.get('lens', '')} lens",
        preset.get("comp", ""),
        preset.get("depth", ""),
    ]
    if camera_motion and camera_motion.lower() not in ("static", ""):
        parts.append(f"{camera_motion} camera movement")

    return ", ".join(filter(None, parts))


# ═══════════════════════════════════════════════════════════════════════════
# 6. Lighting Enricher
# ═══════════════════════════════════════════════════════════════════════════

_LIGHTING_EXPANSIONS: dict[str, list[str]] = {
    "morning":   ["low-angle golden morning rays", "warm amber highlights on surfaces",
                  "soft graduated shadows", "volumetric light columns through windows",
                  "natural lens flare at source"],
    "golden hour": ["magic-hour directional glow", "warm 2700K colour temperature",
                    "long soft shadows", "specular highlights on glass and chrome",
                    "rich saturation without clipping"],
    "natural":   ["soft diffused ambient light", "gentle fill from reflective surfaces",
                  "no harsh shadows", "even skin rendering", "true-to-life colour accuracy"],
    "studio":    ["key light at 45° Rembrandt position", "fill light at 1:3 ratio",
                  "hair light rim separation", "even background gradient",
                  "no ambient contamination"],
    "evening":   ["warm tungsten interior glow", "window shows blue-hour exterior",
                  "contrast between warm inside and cool outside", "candle-flicker quality"],
    "dramatic":  ["chiaroscuro side lighting", "deep shadow pools",
                  "single motivated key source", "high contrast ratio 1:8",
                  "textured shadow patterns"],
}

def _enrich_lighting(environment: dict | None, art: dict | None) -> str:
    """Return a rich lighting descriptor based on environment and art direction."""
    raw_lighting = (environment or {}).get("lighting", "")
    time_of_day  = (environment or {}).get("time_of_day", "")
    combined     = f"{raw_lighting} {time_of_day}".lower()

    for key, descriptors in _LIGHTING_EXPANSIONS.items():
        if key in combined:
            return ", ".join(descriptors[:4])   # top 4 keeps it dense but not bloated

    # Fallback: soft commercial default
    return ("soft diffused key light, subtle fill, natural colour temperature, "
            "gentle specular highlights on premium surfaces")


# ═══════════════════════════════════════════════════════════════════════════
# 7. Style Preset
# ═══════════════════════════════════════════════════════════════════════════

_STYLE_PRESETS: dict[str, str] = {
    "commercial": (
        "commercial photography aesthetic, natural skin rendering, "
        "premium product-photography colour science, luxury lifestyle feel, "
        "realistic materials and textures, high dynamic range, "
        "shallow depth of field, Kodak Portra colour grading"
    ),
    "editorial": (
        "editorial photography, strong graphic composition, "
        "high contrast, fashion-forward colour palette, "
        "intentional negative space, magazine-ready finish"
    ),
    "cinematic": (
        "anamorphic lens character, film grain at 800 ISO, "
        "teal-and-orange complementary grade, "
        "motivated practical lighting, widescreen 2.39:1 crop, "
        "depth through layers of focus"
    ),
    "documentary": (
        "handheld vérité quality, available-light only, "
        "natural colour grading, authentic candid framing, "
        "35mm reportage feel"
    ),
    "product": (
        "hero product photography, 360° studio lighting rig, "
        "flawless surface rendering, controlled reflections, "
        "seamless white or textured backdrop, macro detail"
    ),
}

def _inject_style_preset(art: dict | None, project_type: str = "") -> str:
    """Return the appropriate style preset string."""
    visual_style = (art or {}).get("visual_style", "").lower()
    pt           = project_type.lower()

    if "cinematic" in visual_style:
        return _STYLE_PRESETS["cinematic"]
    if "editorial" in visual_style:
        return _STYLE_PRESETS["editorial"]
    if "documentary" in visual_style:
        return _STYLE_PRESETS["documentary"]
    if "product" in (visual_style + pt):
        return _STYLE_PRESETS["product"]

    # Default: commercial (covers most ad/brand work)
    return _STYLE_PRESETS["commercial"]


# ═══════════════════════════════════════════════════════════════════════════
# 8. Negative Prompt Library (provider-specific)
# ═══════════════════════════════════════════════════════════════════════════

_NEGATIVE_LIBRARY: dict[str, list[str]] = {
    # Flux (both Schnell and Pro)
    "flux": [
        "blurry", "low quality", "low resolution", "pixelated",
        "duplicate limbs", "extra fingers", "malformed hands",
        "bad anatomy", "deformed face", "cross-eyed",
        "text", "watermark", "logo", "signature", "username",
        "cropped", "cut off", "out of frame",
        "oversaturated", "overexposed", "underexposed",
        "grainy noise", "film grain", "artifacts", "compression artifacts",
        "cartoon", "anime", "illustration", "painting", "drawing",
        "unrealistic", "uncanny valley",
    ],
    "sdxl": [
        "ugly", "tiling", "poorly drawn hands", "poorly drawn feet",
        "poorly drawn face", "out of frame", "extra limbs", "disfigured",
        "deformed", "body out of frame", "blurry", "bad anatomy",
        "blurred", "watermark", "grainy", "signature", "cut off",
        "draft", "amateur", "bad proportions",
    ],
    "gpt image": [
        "low quality", "blurry", "watermark", "text overlay",
        "unnatural skin", "distorted features",
    ],
    "imagen": [
        "low quality", "blurry", "artifacts", "watermark",
        "text", "unnatural", "distorted",
    ],
    "veo": [    # Veo 3 / video providers
        "jerky motion", "flickering", "temporal inconsistency",
        "watermark", "text overlay", "low frame rate",
        "compressed artifacts", "abrupt cuts", "jump cuts",
        "overexposed highlights", "crushed blacks",
    ],
    "runway": [
        "stuttering", "watermark", "text", "artifacts",
        "motion blur", "ghosting", "flickering light",
    ],
    # Default fallback
    "default": [
        "blurry", "low quality", "watermark", "text", "artifacts",
        "distorted", "deformed", "cropped",
    ],
}

def get_negative_prompt(provider_name: str, existing: str = "") -> str:
    """Return a provider-specific negative prompt, merging with any existing value."""
    key = provider_name.lower()
    library: list[str] = []

    for provider_key, terms in _NEGATIVE_LIBRARY.items():
        if provider_key in key:
            library = terms
            break

    if not library:
        library = _NEGATIVE_LIBRARY["default"]

    # Merge: existing terms first, then library (deduped)
    existing_terms = [t.strip() for t in existing.split(",") if t.strip()]
    all_terms = existing_terms + [t for t in library if t not in existing_terms]
    return ", ".join(all_terms)


# ═══════════════════════════════════════════════════════════════════════════
# 9. Composition Enricher
# ═══════════════════════════════════════════════════════════════════════════

_COMPOSITION_RULES: dict[str, list[str]] = {
    "wide":        ["rule of thirds applied", "foreground elements frame scene",
                    "leading lines guide eye to subject", "depth through layering"],
    "close":       ["subject occupies 2/3 of frame", "intentional negative space",
                    "texture detail dominant", "background context implied, not shown"],
    "overhead":    ["perfect bilateral symmetry", "props arranged on geometric grid",
                    "negative space balanced on all four sides"],
    "establishing": ["subject small against grand environment", "horizon line at lower third",
                     "sky or ceiling opens upward", "scale communicated"],
    "portrait":    ["eyes on upper third line", "catchlights visible in both eyes",
                    "natural head-room and chin-room", "environment contextual not competing"],
    "default":     ["rule of thirds", "balanced visual weight",
                    "foreground-midground-background separation",
                    "intentional negative space"],
}

def _enrich_composition(generation: dict | None) -> str:
    """Return a composition guidance string based on shot type."""
    shot_type = (generation or {}).get("shot_type", "").lower()

    for key, rules in _COMPOSITION_RULES.items():
        if key in shot_type:
            return ", ".join(rules)

    return ", ".join(_COMPOSITION_RULES["default"])


# ═══════════════════════════════════════════════════════════════════════════
# 10. Emotional Intent
# ═══════════════════════════════════════════════════════════════════════════

_EMOTION_TEMPLATES: dict[str, str] = {
    "warm":       "The viewer immediately feels welcomed, comfortable, and invited into this moment.",
    "luxury":     "The viewer feels an instinctive aspiration — this is the life they deserve.",
    "energetic":  "The viewer feels an immediate surge of energy and forward momentum.",
    "calm":       "The viewer exhales. The world slows. There is peace and space here.",
    "playful":    "The viewer smiles without knowing why — joy is contagious in this frame.",
    "trustworthy": "The viewer feels safe. This brand understands their needs.",
    "exciting":   "The viewer leans forward. Something unmissable is happening right here.",
    "nostalgic":  "The viewer is transported — a bittersweet warmth, like a memory they cherish.",
}

def _add_emotional_intent(emotion: dict | None, brand: dict | None) -> str:
    """Return a high-level viewer-experience directive."""
    # Try emotion plan first, then brand personality
    emotion_str = ""
    if emotion:
        primary = str(emotion.get("primary_emotion", "")).lower()
        for key, template in _EMOTION_TEMPLATES.items():
            if key in primary:
                emotion_str = template
                break

    if not emotion_str and brand:
        personality = str(brand.get("personality", "")).lower()
        for key, template in _EMOTION_TEMPLATES.items():
            if key in personality:
                emotion_str = template
                break

    return emotion_str or "The viewer feels an immediate, genuine human connection with this scene."


# ═══════════════════════════════════════════════════════════════════════════
# Public API
# ═══════════════════════════════════════════════════════════════════════════

def optimize_image_prompt(
    raw_prompt: str,
    resolved: dict[str, Any],
    generation: dict[str, Any] | None = None,
    provider_name: str = "flux",
    existing_negative: str = "",
) -> tuple[str, str]:
    """Run the full optimization pipeline on *raw_prompt*.

    Args:
        raw_prompt:        The concatenated string from prompt_builder.py.
        resolved:          The ``_resolved`` dict (character, environment,
                           brand, art_direction, emotion).
        generation:        The generation spec dict from the job payload
                           (may contain shot_type, camera_motion, etc.).
        provider_name:     Used to select the correct negative-prompt library.
        existing_negative: Any negative prompt already supplied by the plan.

    Returns:
        (optimized_prompt, negative_prompt)  — both ready to send to the adapter.
    """
    char    = resolved.get("character")
    env     = resolved.get("environment")
    brand   = resolved.get("brand")
    art     = resolved.get("art_direction")
    emotion = resolved.get("emotion")
    gen     = generation or {}

    # ── Step 1: De-duplicate the raw builder output ────────────────────────
    prompt = _deduplicate(raw_prompt)

    # ── Step 2: Character enrichment ───────────────────────────────────────
    char_str = _enrich_character(char, raw_prompt)
    if char_str:
        prompt = re.sub(r"Character:[^.]+\.", "", prompt).strip()
        prompt = f"{prompt}. Subject: {char_str}"

    # ── Step 3: Environment enrichment ─────────────────────────────────────
    env_str = _enrich_environment(env)
    if env_str:
        prompt = re.sub(r"Setting:[^.]+\.", "", prompt).strip()
        prompt = f"{prompt}. Location: {env_str}"

    # ── Step 4: Action enrichment ──────────────────────────────────────────
    prompt = _enrich_action(prompt)

    # ── Step 5: Camera enrichment ──────────────────────────────────────────
    cam_str = _enrich_camera(art, gen)
    if cam_str:
        prompt = f"{prompt}. Camera: {cam_str}"

    # ── Step 6: Lighting enrichment ────────────────────────────────────────
    light_str = _enrich_lighting(env, art)
    if light_str:
        prompt = f"{prompt}. Lighting: {light_str}"

    # ── Step 7: Style preset injection ─────────────────────────────────────
    style_str = _inject_style_preset(art)
    prompt = f"{prompt}. Style: {style_str}"

    # ── Step 8: Negative prompt (provider-specific library) ─────────────
    negative = get_negative_prompt(provider_name, existing_negative)

    # ── Step 9: Composition enrichment ─────────────────────────────────────
    comp_str = _enrich_composition(gen)
    if comp_str:
        prompt = f"{prompt}. Composition: {comp_str}"

    # ── Step 10: Emotional intent ──────────────────────────────────────────
    emotion_str = _add_emotional_intent(emotion, brand)
    prompt = f"{prompt}. Intent: {emotion_str}"

    # ── Final cleanup ──────────────────────────────────────────────────────
    prompt = re.sub(r"\s{2,}", " ", prompt)
    prompt = re.sub(r"(\.\s*){2,}", ". ", prompt)
    prompt = prompt.strip()

    logger.info(
        f"[Optimizer] Final prompt: {len(prompt)} chars, "
        f"negative: {len(negative)} chars, "
        f"provider: {provider_name!r}"
    )

    return prompt, negative


def optimize_video_prompt(
    raw_prompt: str,
    resolved: dict[str, Any],
    generation: dict[str, Any] | None = None,
    provider_name: str = "veo",
    existing_negative: str = "",
) -> tuple[str, str]:
    """Video variant — same pipeline but with video-specific negative library."""
    # Reuse image pipeline then append video-specific motion directives
    prompt, negative = optimize_image_prompt(
        raw_prompt=raw_prompt,
        resolved=resolved,
        generation=generation,
        provider_name=provider_name,
        existing_negative=existing_negative,
    )

    camera_motion = (generation or {}).get("camera_motion", "Static")
    duration      = (generation or {}).get("duration", 4)
    fps           = (generation or {}).get("fps", 24)

    motion_spec = (
        f"Motion: {camera_motion} camera movement, "
        f"{fps}fps fluid motion, {duration}s duration, "
        "consistent temporal lighting, no flickering, smooth transitions"
    )
    prompt = f"{prompt}. {motion_spec}"

    return prompt, negative
