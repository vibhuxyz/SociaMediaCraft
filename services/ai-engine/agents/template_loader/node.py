import json
from pathlib import Path

async def template_loader_node(state):
    print("[AI ENGINE] Template Loader Agent running...")
    
    director_plan = state.get("director_plan", {})
    template_name = director_plan.get("template", "Advertisement")
    
    # Map friendly names to file names
    mapping = {
        "advertisement": "advertisement.json",
        "youtube short": "youtube_short.json",
        "instagram reel": "instagram_reel.json",
        "cinematic": "cinematic.json"
    }
    
    clean_name = template_name.lower().strip()
    filename = mapping.get(clean_name, "advertisement.json")
    
    template_path = Path(__file__).parent.parent.parent / "knowledge" / "templates" / filename
    
    template_rules = {}
    if template_path.exists():
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template_rules = json.load(f)
        except Exception as e:
            print(f"[AI ENGINE] Error loading template {filename}: {e}")
    else:
        print(f"[AI ENGINE] Warning: Template file {template_path} not found.")

    return {
        "template_name": template_name,
        "template_rules": template_rules
    }
