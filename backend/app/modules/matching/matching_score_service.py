"""
Service FastAPI de matching — pseudo-code §10.1 (PFE MatiousHire).

La logique peut être intégrée dans un service FastAPI dédié au matching::

    final_score, explanation_data = calculate_matching_score(candidate, job)
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.modules.matching.score_formula import (
    SCORE_WEIGHTS,
    classify_score,
    compute_availability_score,
    compute_education_score,
    compute_location_score,
    compute_semantic_similarity,
    extract_experience_years,
    parse_required_optional_skills,
)
from app.modules.matching.score_formula import (
    compute_experience_score as _formula_experience_score,
)
from app.modules.matching.score_formula import (
    compute_penalties as _compute_penalty_parts,
)
from app.modules.matching.score_formula import (
    compute_skills_score as _compute_skills_score_parts,
)


@dataclass(frozen=True)
class MatchingCandidate:
    """Profil candidat pour le calcul du score (doc. §10.1)."""

    skills: set[str]
    experience_years: float | None = None
    resume_text: str | None = None
    education: str | None = None
    location: str | None = None
    availability: str | None = None
    cv_complete: bool = True
    experience_text: str | None = None


@dataclass(frozen=True)
class MatchingJob:
    """Offre d'emploi pour le calcul du score (doc. §10.1)."""

    required_skills: set[str] = field(default_factory=set)
    optional_skills: set[str] = field(default_factory=set)
    required_experience: float | None = None
    description: str | None = None
    required_education: str | None = None
    location: str | None = None
    remote_policy: str | None = None
    start_date: str | None = None


def get_matched_skills(
    candidate_skills: set[str], required_skills: set[str]
) -> list[str]:
    return sorted(candidate_skills & required_skills)


def get_missing_skills(
    candidate_skills: set[str], required_skills: set[str]
) -> list[str]:
    return sorted(required_skills - candidate_skills)


def compute_skills_score(
    candidate_skills: set[str],
    required_skills: set[str],
    optional_skills: set[str],
) -> float:
    score, _, _, _, _ = _compute_skills_score_parts(
        candidate_skills, required_skills, optional_skills
    )
    return score


def compute_experience_score(
    candidate_experience_years: float | None,
    required_experience: float | None,
) -> float:
    return _formula_experience_score(candidate_experience_years, required_experience)


def compute_penalties(candidate: MatchingCandidate, job: MatchingJob) -> float:
    """Doc. §4.1 — retourne le facteur multiplicatif des pénalités."""
    missing = get_missing_skills(candidate.skills, job.required_skills)
    experience_score = compute_experience_score(
        candidate.experience_years,
        job.required_experience,
    )
    location_score = compute_location_score(
        candidate.location,
        job.location,
        remote_policy=job.remote_policy,
    )
    availability_score = compute_availability_score(
        candidate.availability,
        job.start_date,
    )
    on_site = not (job.remote_policy and "remote" in job.remote_policy.lower())
    factor, _ = _compute_penalty_parts(
        missing_required=missing,
        experience_score=experience_score,
        cv_complete=candidate.cv_complete,
        location_score=location_score,
        availability_score=availability_score,
        on_site_job=on_site and bool(job.location),
    )
    return factor


def calculate_matching_score(
    candidate: MatchingCandidate,
    job: MatchingJob,
) -> tuple[float, dict[str, object]]:
    """
    Pseudo-code doc. §10.1 — calcule le score final et les données d'explication.

    Returns:
        ``(final_score, explanation_data)`` avec ``final_score`` entre 0 et 1.
    """
    if candidate is None or job is None:
        raise ValueError("candidate and job are required for matching score")

    skills_score = compute_skills_score(
        candidate.skills,
        job.required_skills,
        job.optional_skills,
    )
    experience_score = compute_experience_score(
        candidate.experience_years,
        job.required_experience,
    )
    semantic_score = compute_semantic_similarity(
        candidate.resume_text,
        job.description,
    )
    education_score = compute_education_score(
        candidate.education,
        job.required_education or job.description,
    )
    location_score = compute_location_score(
        candidate.location,
        job.location,
        remote_policy=job.remote_policy,
    )
    availability_score = compute_availability_score(
        candidate.availability,
        job.start_date,
    )

    global_score = (
        0.35 * skills_score
        + 0.25 * experience_score
        + 0.20 * semantic_score
        + 0.10 * education_score
        + 0.05 * location_score
        + 0.05 * availability_score
    )

    penalties = compute_penalties(candidate, job)
    final_score = min(max(global_score * penalties, 0.0), 1.0)

    matched_skills = get_matched_skills(candidate.skills, job.required_skills)
    missing_skills = get_missing_skills(candidate.skills, job.required_skills)

    explanation_data: dict[str, object] = {
        "global_score": round(final_score * 100),
        "global_score_before_penalty": round(global_score * 100),
        "skills_score": round(skills_score * 100),
        "experience_score": round(experience_score * 100),
        "semantic_score": round(semantic_score * 100),
        "education_score": round(education_score * 100),
        "location_score": round(location_score * 100),
        "availability_score": round(availability_score * 100),
        "missing_skills": missing_skills,
        "matched_skills": matched_skills,
        "penalty_factor": penalties,
        "rank_label": classify_score(round(final_score * 100)),
        "formula": (
            "S_global = 0.35·S_comp + 0.25·S_exp + 0.20·S_sem + 0.10·S_form "
            "+ 0.05·S_loc + 0.05·S_disp ; S_final = S_global × pénalités"
        ),
        "weights": SCORE_WEIGHTS,
    }

    return final_score, explanation_data


def matching_job_from_raw(
    *,
    required_skills: str | None,
    optional_skills: str | None = None,
    description: str | None = None,
    required_experience: str | None = None,
    required_education: str | None = None,
    location: str | None = None,
    remote_policy: str | None = None,
    start_date: str | None = None,
) -> MatchingJob:
    """Construit un ``MatchingJob`` depuis les champs bruts de la base."""
    required, parsed_optional = parse_required_optional_skills(required_skills)
    optional = parsed_optional
    if optional_skills:
        from app.modules.matching.nlp import split_skill_tokens

        optional = optional | split_skill_tokens(optional_skills)

    exp_years = None
    if required_experience is not None:
        if isinstance(required_experience, (int, float)):
            exp_years = float(required_experience)
        else:
            exp_years = extract_experience_years(required_experience)

    return MatchingJob(
        required_skills=required,
        optional_skills=optional,
        required_experience=exp_years,
        description=description,
        required_education=required_education or description,
        location=location,
        remote_policy=remote_policy,
        start_date=start_date,
    )
