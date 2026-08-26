from dataclasses import dataclass

from app.modules.llm.explanation import (
    build_improvement_tips,
    build_score_justification,
    build_strengths,
    explain_compatibility,
    interview_questions,
    summarize_cv,
    summarize_job,
)
from app.modules.llm.guard import HallucinationGuard
from app.modules.matching.pipeline import MatchingPipeline
from app.modules.matching.scorer import ApplicantProfile, JobProfile, ScoreBreakdown


@dataclass(frozen=True)
class LlmInsight:
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
    confidence_score: int
    grounded: bool
    guard_warnings: list[str]
    grounded_sources: list[str]


LLM_MODULE_INFO = {
    "title": "Module LLM explicable — MatiousHire",
    "version": "1.1.0",
    "approach": "hybrid_grounded",
    "description": (
        "Le module LLM transforme les scores numériques du moteur de matching "
        "en résumés et explications lisibles pour candidats et recruteurs, "
        "avec garde-fous anti-hallucination."
    ),
    "capabilities": [
        "Résumé intelligent du CV",
        "Résumé de l'offre d'emploi",
        "Explication du score de compatibilité",
        "Identification des compétences manquantes",
        "Recommandations d'amélioration du profil",
        "Questions d'entretien suggérées",
        "Validation anti-hallucination et score de confiance",
    ],
    "principles": [
        "Le LLM n'impose pas la décision de recrutement",
        "Chaque explication cite les scores sous-jacents",
        "Les compétences manquantes sont listées explicitement",
        "Le recruteur reste responsable du choix final",
        "Aucun fait généré sans source structurée (CV, offre, scores)",
        "Langage spéculatif filtré ou atténué automatiquement",
    ],
    "anti_hallucination": HallucinationGuard.architecture(),
}


class LlmService:
    DISCLAIMER = (
        "Analyse générée par IA explicable — aide à la décision uniquement. "
        "Contenu ancré sur le CV, l'offre et les scores de matching. "
        "Le recruteur reste responsable de la décision finale."
    )

    @classmethod
    def module_info(cls) -> dict:
        return LLM_MODULE_INFO

    @classmethod
    def analyze(cls, profile: ApplicantProfile, job: JobProfile) -> LlmInsight:
        result = MatchingPipeline.run(profile, job)
        breakdown = result.breakdown
        return cls._insight_from_parts(
            profile, job, result.compatibility_score, breakdown
        )

    @classmethod
    def cv_summary_only(cls, profile: ApplicantProfile) -> str:
        return summarize_cv(profile)

    @classmethod
    def _insight_from_parts(
        cls,
        profile: ApplicantProfile,
        job: JobProfile,
        score: int,
        breakdown: ScoreBreakdown,
    ) -> LlmInsight:
        explanation = explain_compatibility(profile, job, breakdown, score)
        cv_summary = summarize_cv(profile)
        strengths = build_strengths(profile, job, breakdown)

        guard = HallucinationGuard.apply(
            profile=profile,
            job=job,
            breakdown=breakdown,
            explanation=explanation,
            cv_summary=cv_summary,
            strengths=strengths,
        )

        return LlmInsight(
            compatibility_score=score,
            rank_label=MatchingPipeline.rank_label(score),
            explanation=guard.sanitized_explanation,
            cv_summary=guard.sanitized_cv_summary,
            job_summary=summarize_job(job),
            matched_skills=breakdown.matched_skills,
            missing_skills=breakdown.missing_skills,
            strengths=guard.sanitized_strengths,
            score_justification=build_score_justification(breakdown, score),
            improvement_tips=build_improvement_tips(breakdown),
            interview_questions=interview_questions(profile, job, breakdown),
            disclaimer=cls.DISCLAIMER,
            confidence_score=guard.confidence_score,
            grounded=guard.grounded,
            guard_warnings=guard.guard_warnings,
            grounded_sources=guard.grounded_sources,
        )
