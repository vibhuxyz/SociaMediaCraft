from langgraph.graph import StateGraph, END
from workflow.state import CreativeState
from workflow.nodes import (
    art_director_node,
    asset_planner_node,
    audience_localization_node,
    audio_analyzer_node,
    brief_validator_node,
    brand_identity_node,
    casting_director_node,
    character_designer_node,
    cinematography_director_node,
    clarification_agent_node,
    classifier_node,
    commercial_agent_node,
    dialogue_writer_node,
    director_node,
    emotion_analyzer_node,
    environment_designer_node,
    importance_scorer_node,
    knowledge_agent_node,
    missing_info_detector_node,
    music_director_node,
    narration_writer_node,
    production_plan_builder_node,
    prompt_engineering_node,
    quality_review_node,
    screenplay_writer_node,
    shot_planner_node,
    sound_design_director_node,
    story_agent_node,
    storyboard_director_node,
    visual_analyzer_node,
    voice_director_node,
)
from workflow.router import route_after_validator
from langgraph.checkpoint.memory import MemorySaver

    
def build_graph(interrupt_after_clarification: bool = False):

    builder = StateGraph(CreativeState)

    builder.add_node("brief_validator_node", brief_validator_node)
    builder.add_node("director_node", director_node)
    builder.add_node("classifier_node", classifier_node)
    builder.add_node("audio_analyzer_node", audio_analyzer_node)
    builder.add_node("visual_analyzer_node", visual_analyzer_node)
    builder.add_node("missing_info_detector_node", missing_info_detector_node)
    builder.add_node("importance_scorer_node", importance_scorer_node)
    builder.add_node("clarification_agent_node", clarification_agent_node)
    builder.add_node("knowledge_agent_node", knowledge_agent_node)
    builder.add_node("commercial_agent_node", commercial_agent_node)
    builder.add_node("audience_localization_node", audience_localization_node)
    builder.add_node("brand_identity_node", brand_identity_node)
    builder.add_node("casting_director_node", casting_director_node)
    builder.add_node("character_designer_node", character_designer_node)
    builder.add_node("environment_designer_node", environment_designer_node)
    builder.add_node("art_director_node", art_director_node)
    builder.add_node("emotion_analyzer_node", emotion_analyzer_node)
    builder.add_node("story_agent_node", story_agent_node)
    builder.add_node("screenplay_writer_node", screenplay_writer_node)
    builder.add_node("dialogue_writer_node", dialogue_writer_node)
    builder.add_node("narration_writer_node", narration_writer_node)
    builder.add_node("voice_director_node", voice_director_node)
    builder.add_node("music_director_node", music_director_node)
    builder.add_node("sound_design_director_node", sound_design_director_node)
    builder.add_node("storyboard_director_node", storyboard_director_node)
    builder.add_node("cinematography_director_node", cinematography_director_node)
    builder.add_node("shot_planner_node", shot_planner_node)
    builder.add_node("prompt_engineering_node", prompt_engineering_node)
    builder.add_node("asset_planner_node", asset_planner_node)
    builder.add_node("quality_review_node", quality_review_node)
    builder.add_node("production_plan_builder_node", production_plan_builder_node)

    
    builder.set_entry_point("brief_validator_node")
    
    builder.add_conditional_edges("brief_validator_node", route_after_validator)
    
    builder.add_edge("director_node","classifier_node" )
    builder.add_edge("classifier_node", "visual_analyzer_node")
    builder.add_edge("visual_analyzer_node", "audio_analyzer_node")
    builder.add_edge("audio_analyzer_node", "missing_info_detector_node")
    builder.add_edge("missing_info_detector_node", "importance_scorer_node")
    builder.add_edge("importance_scorer_node", "clarification_agent_node")
    builder.add_edge("clarification_agent_node", "knowledge_agent_node")
    builder.add_edge("knowledge_agent_node", "commercial_agent_node")
    builder.add_edge("commercial_agent_node", "audience_localization_node")
    builder.add_edge("audience_localization_node", "brand_identity_node")
    builder.add_edge("brand_identity_node", "casting_director_node")
    builder.add_edge("casting_director_node", "character_designer_node")
    builder.add_edge("character_designer_node", "environment_designer_node")
    builder.add_edge("environment_designer_node", "art_director_node")
    builder.add_edge("art_director_node", "emotion_analyzer_node")
    builder.add_edge("emotion_analyzer_node", "story_agent_node")
    builder.add_edge("story_agent_node", "screenplay_writer_node")
    builder.add_edge("screenplay_writer_node", "dialogue_writer_node")
    builder.add_edge("dialogue_writer_node", "narration_writer_node")
    builder.add_edge("narration_writer_node", "voice_director_node")
    builder.add_edge("voice_director_node", "music_director_node")
    builder.add_edge("music_director_node", "sound_design_director_node")
    builder.add_edge("sound_design_director_node", "storyboard_director_node")
    builder.add_edge("storyboard_director_node", "cinematography_director_node")
    builder.add_edge("cinematography_director_node", "shot_planner_node")
    builder.add_edge("shot_planner_node", "prompt_engineering_node")
    builder.add_edge("prompt_engineering_node", "asset_planner_node")
    builder.add_edge("asset_planner_node", "quality_review_node")
    builder.add_edge("quality_review_node", "production_plan_builder_node")
    builder.add_edge("production_plan_builder_node", END)

    memory = MemorySaver()
    
    interrupt_after = ["clarification_agent_node"] if interrupt_after_clarification else None
    return builder.compile(checkpointer=memory, interrupt_after=interrupt_after)
