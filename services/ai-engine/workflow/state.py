from typing import Optional
from typing_extensions import TypedDict
from agents.common import (
    AudioPlan,
    ArtDirectionPlan,
    AssetPlan,
    AudienceLocalizationPlan,
    BrandIdentityPlan,
    BriefValidationPlan,
    CampaignStrategy,
    CastingPlan,
    CharacterDesignPlan,
    CinematographyPlan,
    ClarificationPlan,
    ClassifierPlan,
    CreativePlan,
    DialoguePlan,
    DirectorPlan,
    EmotionPlan,
    EnvironmentDesignPlan,
    ImportanceScorerPlan,
    KnowledgeResearchPlan,
    NarrationPlan,
    QualityReviewPlan,
    RequirementAnalysisPlan,
    ShotPlan,
    StoryPlan,
    StoryboardPlan,
    VoicePlan,
)
from agents.prompt_engineering.schema import PromptEngineeringPlan

class CreativeState(TypedDict, total=False):
    prompt: str
    template_name: str
    template_rules: dict
    hard_rules: dict[str, list[str]]
    knowledge: dict
    is_valid: bool
    validation_error: Optional[str]
    brief_validation: BriefValidationPlan
    project_type: str
    classifier_plan: ClassifierPlan
    visual_requirements: RequirementAnalysisPlan
    audio_requirements: RequirementAnalysisPlan
    requirements: dict
    visual_missing_information: list[str]
    audio_missing_information: list[str]
    missing_information: list[str]
    critical_missing_information: list[str]
    clarification_answers: dict[str, str]
    clarification_questions: list[str]
    clarification_plan: ClarificationPlan
    director_plan: Optional[DirectorPlan]
    importance_scorer_plan: ImportanceScorerPlan
    knowledge_research: KnowledgeResearchPlan
    campaign_strategy: Optional[CampaignStrategy]
    audience_localization: AudienceLocalizationPlan
    brand_identity: BrandIdentityPlan
    casting: CastingPlan
    character_sheet: CharacterDesignPlan
    environment_sheet: EnvironmentDesignPlan
    art_direction: ArtDirectionPlan
    emotion_plan: EmotionPlan
    story: Optional[StoryPlan]
    screenplay: object
    dialogue: DialoguePlan
    narration: NarrationPlan
    voice_plan: VoicePlan
    audio_plan: AudioPlan
    storyboard: StoryboardPlan
    camera_plan: CinematographyPlan
    shot_plan: ShotPlan
    prompt_pack: PromptEngineeringPlan
    asset_plan: AssetPlan
    quality_report: QualityReviewPlan
    cost_estimation: dict
    
    # State tracking for incremental execution
    invalidated_nodes: list[str]
    creative_plan: CreativePlan
    production_plan: dict
