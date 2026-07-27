import os
from pathlib import Path
from agents.common import KnowledgeSelectorPlan, run_structured_agent

async def knowledge_selector_node(state):
    print("[AI ENGINE] Knowledge Selector Agent running...")
    
    director_plan = state.get("director_plan", {})
    knowledge_dir = Path(__file__).parent.parent.parent / "knowledge"
    
    # 1. Gather all available knowledge files
    available_files = []
    if knowledge_dir.exists():
        for root, _, files in os.walk(knowledge_dir):
            for file in files:
                if file.endswith((".md", ".json")) and "templates" not in root:
                    # Store relative path so LLM sees context like "cinematography/lenses.md"
                    rel_path = os.path.relpath(os.path.join(root, file), knowledge_dir)
                    available_files.append(rel_path)
    
    import time
    start = time.perf_counter()
    
    # 2. Cache Check
    import json
    import hashlib
    
    cache_key_data = json.dumps(director_plan, sort_keys=True)
    cache_key = hashlib.md5(cache_key_data.encode()).hexdigest()
    
    global _KNOWLEDGE_CACHE
    if "_KNOWLEDGE_CACHE" not in globals():
        _KNOWLEDGE_CACHE = {}
        
    if cache_key in _KNOWLEDGE_CACHE:
        print("[AI ENGINE] Knowledge Selector (Python Fast-Path) -> ⚡ USING CACHED RESULT")
        plan = _KNOWLEDGE_CACHE[cache_key]
    else:
        # 3. Build the context for the LLM
        context = (
            f"Director Metadata:\n{director_plan}\n\n"
            f"Available Knowledge Files:\n" + "\n".join(available_files)
        )
        
        # 4. Ask LLM to pick the files
        fallback = KnowledgeSelectorPlan(selected_files=[])
        plan = await run_structured_agent(
            {"context": context}, # fake state just for this prompt
            KnowledgeSelectorPlan,
            "You are the Knowledge Selector Agent. Based on the Director's metadata, choose the most relevant file paths from the Available Knowledge Files list. Return only the EXACT paths from the list.",
            fallback,
        )
        _KNOWLEDGE_CACHE[cache_key] = plan

    # 4. Load the selected files into memory
    knowledge_data = {}
    for rel_path in plan.selected_files:
        full_path = knowledge_dir / rel_path
        if full_path.exists():
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    knowledge_data[rel_path] = f.read()
            except Exception as e:
                print(f"[AI ENGINE] Error reading {rel_path}: {e}")
                
    return {
        "knowledge": knowledge_data
    }
