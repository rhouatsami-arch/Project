from dataclasses import dataclass
from time import perf_counter

from app.modules.matching.scorer import (
    ApplicantProfile,
    JobProfile,
    ScoreBreakdown,
    compatibility_rank_label,
    compute_compatibility_score,
)


@dataclass(frozen=True)
class PipelineStage:
    name: str
    description: str
    technique: str


@dataclass(frozen=True)
class MatchResult:
    compatibility_score: int
    rank_label: str
    breakdown: ScoreBreakdown
    explanation: str


@dataclass(frozen=True)
class StageExecution:
    name: str
    description: str
    technique: str
    duration_ms: float
    status: str = "completed"


@dataclass(frozen=True)
class TracedMatchResult:
    result: MatchResult
    stages: tuple[StageExecution, ...]
    total_duration_ms: float
    algorithms_used: tuple[str, ...] = (
        "skill_dictionary",
        "synonym_embeddings",
        "tfidf_cosine",
        "keyword_overlap",
        "weighted_fusion",
        "rank_sort",
    )


PIPELINE_STAGES: tuple[PipelineStage, ...] = (
    PipelineStage(
        name="collect_profile",
        description="Collecte du profil structuré et du texte brut du CV.",
        technique="Agrégation profil + module d'extraction CV.",
    ),
    PipelineStage(
        name="nlp_preprocessing",
        description="Nettoyage, tokenisation, suppression des stop-words.",
        technique="Regex + filtrage bilingue FR/EN.",
    ),
    PipelineStage(
        name="feature_extraction",
        description="Extraction compétences, embeddings synonymes, TF-IDF.",
        technique="Dictionnaire + embeddings sémantiques + vectorisation.",
    ),
    PipelineStage(
        name="multi_criteria_scoring",
        description="Score multi-critères selon la formule PFE.",
        technique=(
            "0.35 compétences + 0.25 expérience + 0.20 sémantique + "
            "0.10 formation + 0.05 localisation + 0.05 disponibilité"
        ),
    ),
    PipelineStage(
        name="llm_explanation",
        description="Explication lisible avec garde-fou anti-hallucination.",
        technique="LLM explicable + HallucinationGuard (grounding + confiance).",
    ),
    PipelineStage(
        name="ranking",
        description="Classement décroissant des candidats ou offres.",
        technique="Tri par score + libellé de pertinence.",
    ),
)


class MatchingPipeline:
    """Pipeline IA candidat ↔ offre — PFE MatiousHire."""

    WEIGHTS = {
        "skills": 0.35,
        "experience": 0.25,
        "semantic": 0.20,
        "education": 0.10,
        "location": 0.05,
        "availability": 0.05,
    }

    @classmethod
    def stages(cls) -> list[PipelineStage]:
        return list(PIPELINE_STAGES)

    @classmethod
    def run(cls, profile: ApplicantProfile, job: JobProfile) -> MatchResult:
        return cls.run_traced(profile, job).result

    @classmethod
    def run_traced(
        cls, profile: ApplicantProfile, job: JobProfile
    ) -> TracedMatchResult:
        from app.modules.llm.explanation import explain_compatibility

        started = perf_counter()
        executions: list[StageExecution] = []

        def mark(stage: PipelineStage, work) -> object:
            t0 = perf_counter()
            value = work()
            executions.append(
                StageExecution(
                    name=stage.name,
                    description=stage.description,
                    technique=stage.technique,
                    duration_ms=round((perf_counter() - t0) * 1000, 2),
                )
            )
            return value

        stages = {stage.name: stage for stage in PIPELINE_STAGES}

        mark(stages["collect_profile"], lambda: (profile, job))
        mark(
            stages["nlp_preprocessing"],
            lambda: (
                (profile.technical_skills or "")
                + " "
                + (profile.cv_extracted_text or "")
                + " "
                + (job.description or "")
            ).lower(),
        )
        mark(
            stages["feature_extraction"],
            lambda: (
                profile.technical_skills,
                job.required_skills,
                job.title,
            ),
        )
        breakdown: ScoreBreakdown = mark(
            stages["multi_criteria_scoring"],
            lambda: compute_compatibility_score(profile, job),
        )
        score = breakdown.total_score
        label = compatibility_rank_label(score)
        explanation = mark(
            stages["llm_explanation"],
            lambda: explain_compatibility(profile, job, breakdown, score),
        )
        mark(stages["ranking"], lambda: (score, label))

        result = MatchResult(
            compatibility_score=score,
            rank_label=label,
            breakdown=breakdown,
            explanation=explanation,
        )
        return TracedMatchResult(
            result=result,
            stages=tuple(executions),
            total_duration_ms=round((perf_counter() - started) * 1000, 2),
        )

    @staticmethod
    def rank_label(score: int) -> str:
        return compatibility_rank_label(score)
