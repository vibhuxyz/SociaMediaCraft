from langgraph.graph import END
from workflow.state import CreativeState

def route_after_validator(state: CreativeState):
    if state.get("is_valid") == False:
        print(f"❌ VALIDATION FAILED: {state.get('validation_error')}")
        return END
    return ["director_node", "classifier_node", "visual_analyzer_node", "audio_analyzer_node"]

def route_after_classifier(state: CreativeState):
    p_type = state.get("project_type", "")
    if p_type == "Commercial":
        return ["visual_analyzer_node", "audio_analyzer_node","commercial_agent_node"]
    elif p_type == "Story Film":
        return "story_agent_node"
    return END
