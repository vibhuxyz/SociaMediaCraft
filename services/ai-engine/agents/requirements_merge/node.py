import time
from typing import Any

async def requirements_merge_node(state: dict[str, Any]):
    start = time.perf_counter()
    
    clarifications = state.get("clarification_answers", {})
    if not clarifications:
        return {}

    # We want to patch the director_plan with any obvious metadata
    director_plan = state.get("director_plan", {})
    if hasattr(director_plan, "model_dump"):
        director_dict = director_plan.model_dump()
    else:
        director_dict = dict(director_plan)

    # Simple heuristic to map common questions to director_plan fields
    for q, ans in clarifications.items():
        q_lower = q.lower()
        ans_lower = str(ans).lower().strip()
        
        # Normalization
        if ans_lower in ["no", "none", "n/a", "not applicable", "null", "false", "na"]:
            normalized_val = None
        else:
            normalized_val = ans

        if "audience" in q_lower:
            director_dict["target_audience"] = normalized_val
        elif "brand" in q_lower or "name" in q_lower:
            if normalized_val is not None:
                director_dict["brand_name"] = normalized_val
                # Override original prompt to prevent confusion downstream
                state["prompt"] = f"{state.get('prompt', '')} (Brand Name: {normalized_val})"
        elif "duration" in q_lower or "length" in q_lower:
            director_dict["duration"] = normalized_val
        elif "country" in q_lower or "location" in q_lower:
            director_dict["country"] = normalized_val
        elif "accent" in q_lower or "voice" in q_lower:
            director_dict["accent"] = normalized_val

    # Consolidate visual and audio requirements
    unified_reqs = {
        "known": [],
        "missing": []
    }
    
    # Extract from existing state
    vis_reqs = state.get("visual_requirements", {})
    aud_reqs = state.get("audio_requirements", {})
    
    vis_known = vis_reqs.get("known", []) if isinstance(vis_reqs, dict) else getattr(vis_reqs, "known", [])
    aud_known = aud_reqs.get("known", []) if isinstance(aud_reqs, dict) else getattr(aud_reqs, "known", [])
    
    for k in vis_known + aud_known:
        # Pydantic or dict check
        k_dict = k if isinstance(k, dict) else (k.model_dump() if hasattr(k, "model_dump") else dict(k))
        if k_dict not in unified_reqs["known"]:
            unified_reqs["known"].append(k_dict)
            
    # Add new answers directly to known!
    for q, ans in clarifications.items():
        ans_lower = str(ans).lower().strip()
        if ans_lower not in ["no", "none", "n/a", "not applicable", "null", "false", "na"]:
            unified_reqs["known"].append({"name": q, "value": ans})

    end = time.perf_counter()
    print(f"[AI ENGINE] Requirements Merge (Python Fast-Path) took {end-start:.4f}s")
    
    return {"director_plan": director_dict, "prompt": state.get("prompt", ""), "requirements": unified_reqs}
