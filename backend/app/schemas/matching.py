from pydantic import BaseModel, Field

from app.schemas.recruitment import JobOut


class ScoreBreakdownOut(BaseModel):
    skills_score: int = Field(description="Score compétences (0-100)")
    experience_score: int = Field(description="Score expérience (0-100)")
    semantic_score: int = Field(description="Score sémantique TF-IDF (0-100)")
    education_score: int = Field(description="Score formation (0-100)")
    location_score: int = Field(description="Score localisation (0-100)")
    availability_score: int = Field(description="Score disponibilité (0-100)")
    matched_skills: list[str]
    missing_skills: list[str]
    matched_optional_skills: list[str] = Field(default_factory=list)
    missing_optional_skills: list[str] = Field(default_factory=list)
    global_score_before_penalty: int | None = None
    penalty_factor: float = 1.0
    penalties_applied: list[str] = Field(default_factory=list)


class LlmExplanationOut(BaseModel):
    compatibility_score: int
    rank_label: str
    explanation: str
    cv_summary: str
    job_summary: str
    matched_skills: list[str]
    missing_skills: list[str]
    strengths: list[str]
    score_justification: str
    improvement_tips: list[str]
    interview_questions: list[str]
    disclaimer: str
    confidence_score: int = Field(
        ge=0, le=100, description="Fiabilité de l'explication (anti-hallucination)"
    )
    grounded: bool = Field(description="Explication validée contre les sources")
    guard_warnings: list[str] = Field(default_factory=list)
    grounded_sources: list[str] = Field(default_factory=list)


class LlmModuleInfoOut(BaseModel):
    title: str
    version: str
    approach: str
    description: str
    capabilities: list[str]
    principles: list[str]
    anti_hallucination: dict = Field(default_factory=dict)


class CvSummaryOut(BaseModel):
    summary: str


class MatchResultOut(BaseModel):
    compatibility_score: int = Field(ge=0, le=100)
    rank_label: str
    breakdown: ScoreBreakdownOut
    explanation: str


class JobRecommendationOut(BaseModel):
    job: JobOut
    compatibility_score: int
    rank_label: str
    breakdown: ScoreBreakdownOut
    explanation: str


class CandidateRankingOut(BaseModel):
    application_id: int
    student_id: str
    first_name: str
    last_name: str
    email: str
    compatibility_score: int
    rank: int
    rank_label: str
    breakdown: ScoreBreakdownOut
    explanation: str


class PipelineStageOut(BaseModel):
    name: str
    description: str
    technique: str


class PipelineStageExecutionOut(BaseModel):
    name: str
    description: str
    technique: str
    duration_ms: float
    status: str = "completed"


class PipelineInfoOut(BaseModel):
    title: str
    version: str
    description: str
    formula: str
    weights: dict[str, float]
    stages: list[PipelineStageOut]
    algorithms: list[str]
    rank_labels: dict[str, str]


class PipelineRunOut(BaseModel):
    compatibility_score: int
    rank_label: str
    breakdown: ScoreBreakdownOut
    explanation: str
    stages: list[PipelineStageExecutionOut]
    total_duration_ms: float
    algorithms_used: list[str]


class MatchScoreRequest(BaseModel):
    technical_skills: str | None = None
    soft_skills: str | None = None
    skills: str | None = None
    cv_extracted_text: str | None = None
    field_of_study: str | None = None
    experiences: str | None = None
    projects: str | None = None
    bio: str | None = None
    internship_type: str | None = None
    location: str | None = None
    job_title: str
    job_description: str
    required_skills: str | None = None
    optional_skills: str | None = None
    job_location: str | None = None
    employment_type: str | None = None
    trace: bool = False


class MatchingCalculateOut(BaseModel):
    """Réponse alignée sur le pseudo-code doc. §10.1."""

    final_score: float = Field(ge=0, le=1, description="Score final entre 0 et 1")
    explanation_data: dict[str, object]
