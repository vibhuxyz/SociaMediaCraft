from typing import Optional
from typing_extensions import TypedDict
from agents.common import (
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
    MusicPlan,
    NarrationPlan,
    PromptEngineeringPlan,
    QualityReviewPlan,
    RequirementAnalysisPlan,
    ShotPlan,
    SoundDesignPlan,
    StoryPlan,
    StoryboardPlan,
    VoicePlan,
)

class CreativeState(TypedDict, total=False):
    prompt: str
    is_valid: bool
    validation_error: Optional[str]
    brief_validation: BriefValidationPlan
    project_type: str
    classifier_plan: ClassifierPlan
    visual_requirements: RequirementAnalysisPlan
    audio_requirements: RequirementAnalysisPlan
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
    music_plan: MusicPlan
    sound_design: SoundDesignPlan
    storyboard: StoryboardPlan
    camera_plan: CinematographyPlan
    shot_plan: ShotPlan
    prompt_pack: PromptEngineeringPlan
    asset_plan: AssetPlan
    quality_report: QualityReviewPlan
    creative_plan: CreativePlan
    production_plan: dict
