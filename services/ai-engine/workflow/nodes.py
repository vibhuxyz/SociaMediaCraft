from agents.brief_validator.node import brief_validator_node
from agents.director.node import director_node
from agents.classifier.node import classifier_node
from agents.campaign_strategy.node import commercial_agent_node
from agents.story_architect.node import story_agent_node
from agents.requirement_analyzer.node import visual_analyzer_node, audio_analyzer_node
from agents.missing_info_detector.node import missing_info_detector_node
from agents.importance_scorer.node import importance_scorer_node
from agents.clarification_agent.node import clarification_agent_node
from agents.knowledge_agent.node import knowledge_agent_node
from agents.audience_localization.node import audience_localization_node
from agents.brand_identity.node import brand_identity_node
from agents.casting_director.node import casting_director_node
from agents.character_designer.node import character_designer_node
from agents.environment_designer.node import environment_designer_node
from agents.art_director.node import art_director_node
from agents.emotion_analyzer.node import emotion_analyzer_node
from agents.screenplay_writer.node import screenplay_writer_node
from agents.dialogue_planner.node import dialogue_planner_node
from agents.narration_planner.node import narration_planner_node
from agents.voice_director.node import voice_director_node
from agents.audio_director.node import audio_director_node
from agents.storyboard_director.node import storyboard_director_node
from agents.cinematography_director.node import cinematography_director_node
from agents.shot_planner.node import shot_planner_node
from agents.prompt_engineering.node import prompt_engineering_node
from agents.asset_planner.node import asset_planner_node
from agents.quality_review.node import quality_review_node
from agents.production_plan_builder.node import production_plan_builder_node

# This file now acts purely as an export barrel to keep imports clean for graph.py!
from agents.template_loader.node import template_loader_node
from agents.knowledge_selector.node import knowledge_selector_node
from agents.rule_engine.node import rule_engine_node
from agents.cost_estimator.node import cost_estimator_node
from agents.requirements_merge.node import requirements_merge_node

from agents.action_complexity_analyzer.node import action_complexity_analyzer_node
from agents.object_interaction_analyzer.node import object_interaction_analyzer_node
from agents.motion_planner.node import motion_planner_node

from workflow.registry import agent_registry

# Explicit Registration (Some nodes have internal decorators, the registry will safely ignore these double registrations)
agent_registry.register("brief_validator_node")(brief_validator_node)
agent_registry.register("director_node")(director_node)
agent_registry.register("classifier_node")(classifier_node)
agent_registry.register("commercial_agent_node")(commercial_agent_node)
agent_registry.register("story_agent_node")(story_agent_node)
agent_registry.register("visual_analyzer_node")(visual_analyzer_node)
agent_registry.register("audio_analyzer_node")(audio_analyzer_node)
agent_registry.register("missing_info_detector_node")(missing_info_detector_node)
agent_registry.register("importance_scorer_node")(importance_scorer_node)
agent_registry.register("clarification_agent_node")(clarification_agent_node)
agent_registry.register("knowledge_agent_node")(knowledge_agent_node)
agent_registry.register("audience_localization_node")(audience_localization_node)
agent_registry.register("brand_identity_node")(brand_identity_node)
agent_registry.register("casting_director_node")(casting_director_node)
agent_registry.register("character_designer_node")(character_designer_node)
agent_registry.register("environment_designer_node")(environment_designer_node)
agent_registry.register("art_director_node")(art_director_node)
agent_registry.register("emotion_analyzer_node")(emotion_analyzer_node)
agent_registry.register("screenplay_writer_node")(screenplay_writer_node)
agent_registry.register("dialogue_planner_node")(dialogue_planner_node)
agent_registry.register("narration_planner_node")(narration_planner_node)
agent_registry.register("voice_director_node")(voice_director_node)
agent_registry.register("audio_director_node")(audio_director_node)
agent_registry.register("storyboard_director_node")(storyboard_director_node)
agent_registry.register("cinematography_director_node")(cinematography_director_node)
agent_registry.register("shot_planner_node")(shot_planner_node)
agent_registry.register("prompt_engineering_node")(prompt_engineering_node)
agent_registry.register("asset_planner_node")(asset_planner_node)
agent_registry.register("quality_review_node")(quality_review_node)
agent_registry.register("production_plan_builder_node")(production_plan_builder_node)
agent_registry.register("template_loader_node")(template_loader_node)
agent_registry.register("knowledge_selector_node")(knowledge_selector_node)
agent_registry.register("rule_engine_node")(rule_engine_node)
agent_registry.register("cost_estimator_node")(cost_estimator_node)
agent_registry.register("requirements_merge_node")(requirements_merge_node)
agent_registry.register("action_complexity_analyzer_node")(action_complexity_analyzer_node)
agent_registry.register("object_interaction_analyzer_node")(object_interaction_analyzer_node)
agent_registry.register("motion_planner_node")(motion_planner_node)
