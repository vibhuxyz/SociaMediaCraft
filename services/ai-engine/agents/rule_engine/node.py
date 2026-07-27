async def rule_engine_node(state):
    print("[AI ENGINE] Rule Engine Agent running...")
    
    template_rules = state.get("template_rules", {})
    hard_rules = template_rules.get("hard_rules", {})
    
    if not isinstance(hard_rules, dict):
        hard_rules = {}

    # We can also dynamically generate rules based on metadata if needed
    director_plan = state.get("director_plan", {})
    if isinstance(director_plan, dict):
        duration = director_plan.get("duration") or template_rules.get("duration")
    else:
        duration = getattr(director_plan, "duration", template_rules.get("duration"))
        
    if duration:
        if "Story Architect" not in hard_rules:
            hard_rules["Story Architect"] = []
        hard_rules["Story Architect"].append(f"STRICT DURATION LIMIT: {duration}")
        
    scene_limit = template_rules.get("scene_limit")
    if scene_limit:
        if "Cinematography Director" not in hard_rules:
            hard_rules["Cinematography Director"] = []
        hard_rules["Cinematography Director"].append(f"STRICT SCENE LIMIT: Maximum {scene_limit} scenes allowed")
        
    return {
        "hard_rules": hard_rules
    }
