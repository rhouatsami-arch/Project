"""Anti-hallucination guard for the explainable LLM module.

Architecture (PFE MatiousHire):
    Matching scores (source of truth)
        -> Template explanation (grounded generation)
        -> HallucinationGuard (validation + confidence)
        -> API response with traceability metadata

The guard never invents facts: it validates that generated text stays within
evidence extracted from the candidate profile, job offer, and score breakdown.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.modules.matching.nlp import split_skill_tokens
from app.modules.matching.scorer import ApplicantProfile, JobProfile, ScoreBreakdown

SPECULATIVE_PATTERNS = (
    re.compile(r"\b(sans doute|certainement|à coup sûr|garanti|parfait pour)\b", re.I),
    re.compile(r"\b(expert mondial|leader|numéro 1|meilleur candidat)\b", re.I),
)

SOFTENING_REPLACEMENTS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b(sans doute|certainement|à coup sûr)\b", re.I), "potentiellement"),
    (re.compile(r"\b(garanti|parfait pour)\b", re.I), "compatible avec"),
    (
        re.compile(r"\b(expert mondial|leader|numéro 1|meilleur candidat)\b", re.I),
        "profil adapté",
    ),
)


@dataclass(frozen=True)
class GuardResult:
    confidence_score: int
    grounded: bool
    guard_warnings: list[str]
    grounded_sources: list[str]
    sanitized_explanation: str
    sanitized_cv_summary: str
    sanitized_strengths: list[str]


@dataclass
class EvidenceCorpus:
    profile_fields: list[str] = field(default_factory=list)
    job_fields: list[str] = field(default_factory=list)
    score_fields: list[str] = field(default_factory=list)
    allowed_skills: set[str] = field(default_factory=set)
    allowed_tokens: set[str] = field(default_factory=set)


class HallucinationGuard:
    """Validates and sanitizes LLM outputs against structured evidence."""

    MIN_CONFIDENCE = 45
    ARCHITECTURE = {
        "strategy": "grounded_hybrid",
        "layers": [
            {
                "name": "source_of_truth",
                "role": "Les scores NLP/matching sont la seule base numérique.",
                "inputs": ["ApplicantProfile", "JobProfile", "ScoreBreakdown"],
            },
            {
                "name": "grounded_generation",
                "role": "Templates et règles — pas de génération libre non contrôlée.",
                "inputs": ["matched_skills", "missing_skills", "dimension scores"],
            },
            {
                "name": "hallucination_guard",
                "role": "Validation, filtrage lexical et score de confiance.",
                "checks": [
                    "skills_whitelist",
                    "speculative_language_filter",
                    "data_completeness",
                    "score_traceability",
                ],
            },
            {
                "name": "human_in_the_loop",
                "role": "Disclaimer + recruteur décisionnaire final.",
                "outputs": ["disclaimer", "guard_warnings", "confidence_score"],
            },
        ],
        "principles": [
            "Pas de fait sans source structurée (CV, offre, breakdown).",
            "Pas de compétence mentionnée hors liste autorisée.",
            "Langage spéculatif atténué ou signalé.",
            "Abstention partielle si données CV incomplètes.",
            "Chaque score cité est traçable vers le moteur de matching.",
        ],
    }

    @classmethod
    def architecture(cls) -> dict:
        return cls.ARCHITECTURE

    @classmethod
    def build_corpus(
        cls,
        profile: ApplicantProfile,
        job: JobProfile,
        breakdown: ScoreBreakdown,
    ) -> EvidenceCorpus:
        profile_fields = [
            name
            for name, value in (
                ("technical_skills", profile.technical_skills),
                ("soft_skills", profile.soft_skills),
                ("field_of_study", profile.field_of_study),
                ("experiences", profile.experiences),
                ("projects", profile.projects),
                ("certifications", profile.certifications),
                ("bio", profile.bio),
                ("location", profile.location),
                ("internship_type", profile.internship_type),
                ("cv_extracted_text", profile.cv_extracted_text),
            )
            if value and str(value).strip()
        ]
        job_fields = [
            name
            for name, value in (
                ("title", job.title),
                ("description", job.description),
                ("required_skills", job.required_skills),
                ("location", job.location),
                ("employment_type", job.employment_type),
            )
            if value and str(value).strip()
        ]
        score_fields = [
            "skills_score",
            "experience_score",
            "semantic_score",
            "education_score",
            "location_score",
            "availability_score",
            "matched_skills",
            "missing_skills",
        ]

        allowed_skills = {
            *(breakdown.matched_skills or []),
            *(breakdown.missing_skills or []),
            *(breakdown.matched_optional_skills or []),
            *(breakdown.missing_optional_skills or []),
        }
        for blob in (
            profile.technical_skills,
            profile.soft_skills,
            profile.skills,
            job.required_skills,
        ):
            allowed_skills.update(split_skill_tokens(blob or ""))

        allowed_tokens: set[str] = set()
        for blob in (
            profile.technical_skills,
            profile.soft_skills,
            profile.experiences,
            profile.projects,
            profile.certifications,
            profile.bio,
            profile.field_of_study,
            profile.cv_extracted_text,
            job.title,
            job.description,
            job.required_skills,
        ):
            if not blob:
                continue
            allowed_tokens.update(re.findall(r"[a-z0-9+#.]{3,}", blob.lower()))

        return EvidenceCorpus(
            profile_fields=profile_fields,
            job_fields=job_fields,
            score_fields=score_fields,
            allowed_skills={s.lower() for s in allowed_skills if s},
            allowed_tokens=allowed_tokens,
        )

    @classmethod
    def _soften_speculative_language(cls, text: str) -> tuple[str, list[str]]:
        warnings: list[str] = []
        sanitized = text
        for pattern in SPECULATIVE_PATTERNS:
            if pattern.search(sanitized):
                warnings.append(
                    "Langage spéculatif détecté et atténué "
                    "pour éviter une sur-interprétation."
                )
                break
        for pattern, replacement in SOFTENING_REPLACEMENTS:
            sanitized = pattern.sub(replacement, sanitized)
        return sanitized, warnings

    @classmethod
    def _find_ungrounded_skills(cls, text: str, corpus: EvidenceCorpus) -> list[str]:
        mentioned = split_skill_tokens(text)
        ungrounded: list[str] = []
        for skill in mentioned:
            key = skill.lower()
            if key in corpus.allowed_skills:
                continue
            if key in corpus.allowed_tokens:
                continue
            if len(key) <= 2:
                continue
            ungrounded.append(skill)
        return ungrounded

    @classmethod
    def _compute_confidence(
        cls,
        profile: ApplicantProfile,
        breakdown: ScoreBreakdown,
        corpus: EvidenceCorpus,
        warnings: list[str],
    ) -> int:
        filled = len(corpus.profile_fields)
        completeness = min(filled / 6, 1.0)
        penalty = breakdown.penalty_factor if breakdown.penalty_factor else 1.0
        semantic = breakdown.semantic_score
        warning_penalty = min(len(warnings) * 0.08, 0.35)
        raw = (
            (0.45 * completeness)
            + (0.35 * semantic)
            + (0.20 * penalty)
            - warning_penalty
        )
        if not profile.cv_extracted_text and not profile.experiences:
            raw -= 0.12
        return max(0, min(100, round(raw * 100)))

    @classmethod
    def _filter_strengths(
        cls, strengths: list[str], corpus: EvidenceCorpus
    ) -> tuple[list[str], list[str]]:
        warnings: list[str] = []
        filtered: list[str] = []
        for item in strengths:
            ungrounded = cls._find_ungrounded_skills(item, corpus)
            if ungrounded:
                warnings.append(
                    "Point fort filtré (compétence non vérifiable): "
                    + ", ".join(ungrounded[:3])
                )
                continue
            filtered.append(item)
        if not filtered:
            filtered.append(
                "Analyse basée uniquement sur les données structurées disponibles."
            )
        return filtered, warnings

    @classmethod
    def apply(
        cls,
        *,
        profile: ApplicantProfile,
        job: JobProfile,
        breakdown: ScoreBreakdown,
        explanation: str,
        cv_summary: str,
        strengths: list[str],
    ) -> GuardResult:
        corpus = cls.build_corpus(profile, job, breakdown)
        warnings: list[str] = []

        explanation, spec_warnings = cls._soften_speculative_language(explanation)
        warnings.extend(spec_warnings)

        cv_summary, cv_spec = cls._soften_speculative_language(cv_summary)
        warnings.extend(cv_spec)

        for label, text in (("explication", explanation), ("résumé CV", cv_summary)):
            ungrounded = cls._find_ungrounded_skills(text, corpus)
            if ungrounded:
                warnings.append(
                    f"{label.capitalize()}: compétences non ancrées dans les sources — "
                    + ", ".join(ungrounded[:4])
                )

        strengths, strength_warnings = cls._filter_strengths(strengths, corpus)
        warnings.extend(strength_warnings)

        confidence = cls._compute_confidence(profile, breakdown, corpus, warnings)
        grounded = confidence >= cls.MIN_CONFIDENCE and not any(
            "non ancrées" in w for w in warnings
        )

        if confidence < cls.MIN_CONFIDENCE:
            warnings.append(
                "Confiance faible: données CV/offre incomplètes — "
                "interprétation prudente."
            )
            explanation += (
                " Note: analyse limitée par le volume de données disponibles; "
                "compléter le profil améliore la fiabilité."
            )

        grounded_sources = [
            f"profile:{name}" for name in corpus.profile_fields
        ] + [f"job:{name}" for name in corpus.job_fields] + [
            f"score:{name}" for name in corpus.score_fields
        ]

        return GuardResult(
            confidence_score=confidence,
            grounded=grounded,
            guard_warnings=list(dict.fromkeys(warnings)),
            grounded_sources=grounded_sources,
            sanitized_explanation=explanation,
            sanitized_cv_summary=cv_summary,
            sanitized_strengths=strengths,
        )
