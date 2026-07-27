from langgraph.graph import StateGraph, END
from workflow.state import CreativeState
from workflow.registry import agent_registry
from workflow.router import route_after_validator
from langgraph.checkpoint.memory import MemorySaver
# Ensure nodes are registered
import workflow.nodes

def route_after_clarification(state: CreativeState):
    # Always route to the next node.
    # If interrupt_after_clarification is True, LangGraph will automatically yield BEFORE hitting this node.
    return "template_loader_node"

def build_graph(interrupt_after_clarification: bool = False):
    builder = StateGraph(CreativeState)

    # Dynamically inject all registered agents into the graph!
    for name, func in agent_registry.get_all_agents().items():
        builder.add_node(name, func)

    
    builder.set_entry_point("brief_validator_node")
    
    builder.add_conditional_edges("brief_validator_node", route_after_validator)
    



    
    # Converge at Missing Info Detector
    builder.add_edge([
        "director_node",
        "classifier_node",
        "visual_analyzer_node",
        "audio_analyzer_node"
    ], "missing_info_detector_node")
    
    # The rest of the setup sequence
    builder.add_edge("missing_info_detector_node", "importance_scorer_node")
    builder.add_edge("importance_scorer_node", "clarification_agent_node")
    
    builder.add_conditional_edges(
        "clarification_agent_node", 
        route_after_clarification,
        {
            END: END,
            "template_loader_node": "template_loader_node"
        }
    )
    
    builder.add_edge("template_loader_node", "requirements_merge_node")
    builder.add_edge("requirements_merge_node", "rule_engine_node")
    builder.add_edge("rule_engine_node", "knowledge_selector_node")

    # --- PARALLEL GROUP 1: Foundation ---
    # These do not depend on each other and can run in parallel
    builder.add_edge("knowledge_selector_node", "commercial_agent_node")
    builder.add_edge("knowledge_selector_node", "audience_localization_node")
    builder.add_edge("knowledge_selector_node", "brand_identity_node")
    builder.add_edge("knowledge_selector_node", "environment_designer_node")
    builder.add_edge("knowledge_selector_node", "art_director_node")
    builder.add_edge("knowledge_selector_node", "emotion_analyzer_node")
    builder.add_edge("knowledge_selector_node", "casting_director_node")
    # Audio Director now runs parallel here instead of waiting for narration
    builder.add_edge("knowledge_selector_node", "audio_director_node")
    
    # Sub-branch: Character Designer needs Casting
    builder.add_edge("casting_director_node", "character_designer_node")

    # --- CONVERGE: Story Agent ---
    builder.add_edge([
        "commercial_agent_node",
        "audience_localization_node",
        "brand_identity_node",
        "environment_designer_node",
        "art_director_node",
        "emotion_analyzer_node",
        "character_designer_node"
    ], "story_agent_node")

    # --- PARALLEL GROUP 2: Audio & Visual Planning ---
    builder.add_edge("story_agent_node", "screenplay_writer_node")
    
    # Audio & Voice branch
    builder.add_edge("screenplay_writer_node", "voice_director_node")
    builder.add_edge("voice_director_node", "dialogue_planner_node")
    builder.add_edge("voice_director_node", "narration_planner_node")
    
    # Storyboard converges from voice/audio and screenplay
    builder.add_edge([
        "dialogue_planner_node",
        "narration_planner_node",
        "audio_director_node"
    ], "storyboard_director_node")

    # --- FINAL LINEAR SEQUENCE ---
    builder.add_edge("storyboard_director_node", "cinematography_director_node")
    builder.add_edge("cinematography_director_node", "shot_planner_node")
    builder.add_edge("shot_planner_node", "action_complexity_analyzer_node")
    builder.add_edge("action_complexity_analyzer_node", "object_interaction_analyzer_node")
    builder.add_edge("object_interaction_analyzer_node", "motion_planner_node")
    builder.add_edge("motion_planner_node", "prompt_engineering_node")
    builder.add_edge("prompt_engineering_node", "asset_planner_node")
    builder.add_edge("asset_planner_node", "quality_review_node")
    builder.add_edge("quality_review_node", "cost_estimator_node")
    builder.add_edge("cost_estimator_node", "production_plan_builder_node")
    builder.add_edge("production_plan_builder_node", END)

    memory = MemorySaver()
    
    interrupt_after = []
    if interrupt_after_clarification:
        interrupt_after.append("clarification_agent_node")
        
    return builder.compile(checkpointer=memory, interrupt_after=interrupt_after)
