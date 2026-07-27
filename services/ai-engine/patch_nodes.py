import os
import glob
import re

for filepath in glob.glob("agents/*/node.py"):
    with open(filepath, "r") as f:
        content = f.read()
    
    # Extract the return key, e.g. return {"music_plan": plan}
    match = re.search(r'return\s+\{"([^"]+)":\s*(?:plan|output)\}', content)
    if not match:
        continue
        
    state_key = match.group(1)
    
    # Check if run_structured_agent is called without state_key
    if "state_key=" not in content:
        # We need to insert state_key="xyz" into the run_structured_agent call
        # It usually looks like:
        #     fallback_obj,
        # )
        # or
        #     Fallback(),
        # )
        
        # We can find the closing parenthesis of run_structured_agent
        content = re.sub(
            r'(run_structured_agent\s*\([^)]+,\s*[^)]+,\s*[^)]+,\s*[^)]+)(\s*\))',
            rf'\1,\n        state_key="{state_key}"\2',
            content
        )
        
        with open(filepath, "w") as f:
            f.write(content)
            
print("Nodes patched!")
