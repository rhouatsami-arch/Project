from dataclasses import dataclass

from app.modules.cv.skills import extract_skills_from_text
from app.modules.matching.matching_score_service import (
    MatchingCandidate,
    MatchingJob,
    calculate_matching_score,
    matching_job_from_raw,
)
from app.modules.matching.nlp import split_skill_tokens
from app.modules.matching.score_formula import classify_score, extract_experience_years


@dataclass(frozen=True)
class ApplicantProfile:
    technical_skills: str | None = None
    soft_skills: str | None = None
    skills: str | None = None
    cv_extracted_text: str | None = None
    field_of_study: str | None = None
    experiences: str | None = None
    projects: str | None = None
    bio: str | None = None
    certifications: str | None = None
    languages: str | None = None
    internship_type: str | None = None
    internship_duration: str | None = None
    location: str | None = None
    availability: str | None = None
    experience_years: float | None = None


@dataclass(frozen=True)
class JobProfile:
    title: str
    description: str
    required_skills: str | None = None
    optional_skills: str | None = None
    location: str | None = None
    employment_type: str | None = None
    remote_policy: str | None = None
    required_experience: str | None = None
    required_education: str | None = None
    start_date_hint: str | None = None


@dataclass(frozen=True)
class ScoreBreakdown:
    skills_score: float
    experience_score: float
    semantic_score: float
    education_score: float
    location_score: float
    availability_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    matched_optional_skills: list[str] | None = None
    missing_optional_skills: list[str] | None = None
    global_score_before_penalty: float | None = None
    penalty_factor: float = 1.0
    penalties_applied: list[str] | None = None
    explanation_data: dict[str, object] | None = None

    @property
    def total_score(self) -> int:
        if self.explanation_data and "global_score" in self.explanation_data:
            return int(self.explanation_data["global_score"])
        weighted = (
            self.skills_score * 0.35
            + self.experience_score * 0.25
            + self.semantic_score * 0.20
            + self.education_score * 0.10
            + self.location_score * 0.05
            + self.availability_score * 0.05
        )
        factor = self.penalty_factor if self.penalty_factor else 1.0
        return round(min(max(weighted * factor, 0.0), 1.0) * 100)


def _profile_skill_set(profile: ApplicantProfile) -> set[str]:
    explicit = (
        split_skill_tokens(profile.technical_skills)
        | split_skill_tokens(profile.soft_skills)
        | split_skill_tokens(profile.skills)
    )
    corpus = " ".join(
        part
        for part in [
            profile.technical_skills,
            profile.soft_skills,
            profile.skills,
            profile.cv_extracted_text,
            profile.experiences,
            profile.projects,
            profile.bio,
        ]
        if part
    )
    detected = set(extract_skills_from_text(corpus))
    return {skill.lower() for skill in explicit | detected}


def _profile_corpus(profile: ApplicantProfile) -> str:
    return "\n".join(
        part
        for part in [
            profile.technical_skills,
            profile.soft_skills,
            profile.skills,
            profile.cv_extracted_text,
            profile.experiences,
            profile.projects,
            profile.bio,
            profile.field_of_study,
            profile.certifications,
        ]
        if part
    )


def _experience_text(profile: ApplicantProfile) -> str:
    return " ".join(
        part for part in [profile.experiences, profile.projects, profile.bio] if part
    )


def _cv_is_complete(profile: ApplicantProfile) -> bool:
    filled = sum(
        1
        for value in [
            profile.technical_skills,
            profile.cv_extracted_text,
            profile.experiences,
            profile.field_of_study,
        ]
        if value and value.strip()
    )
    return filled >= 3


def _to_matching_candidate(profile: ApplicantProfile) -> MatchingCandidate:
    experience_text = _experience_text(profile)
    years = profile.experience_years
    if years is None:
        years = extract_experience_years(experience_text)

    availability_hint = " ".join(
        part
        for part in [
            profile.availability,
            profile.internship_type,
            profile.internship_duration,
        ]
        if part
    )

    return MatchingCandidate(
        skills=_profile_skill_set(profile),
        experience_years=years,
        resume_text=_profile_corpus(profile),
        education=profile.field_of_study,
        location=profile.location,
        availability=availability_hint or None,
        cv_complete=_cv_is_complete(profile),
        experience_text=experience_text or None,
    )


def _to_matching_job(job: JobProfile) -> MatchingJob:
    return matching_job_from_raw(
        required_skills=job.required_skills,
        optional_skills=job.optional_skills,
        description=f"{job.title}\n{job.description}",
        required_experience=job.required_experience or job.description,
        required_education=job.required_education or job.description,
        location=job.location,
        remote_policy=job.remote_policy or job.employment_type,
        start_date=job.start_date_hint,
    )


def compute_compatibility_score(
    profile: ApplicantProfile, job: JobProfile
) -> ScoreBreakdown:
    """Calcule le score via le service doc. §10.1 ``calculate_matching_score``."""
    candidate = _to_matching_candidate(profile)
    matching_job = _to_matching_job(job)
    _final_score, explanation_data = calculate_matching_score(candidate, matching_job)

    return ScoreBreakdown(
        skills_score=float(explanation_data["skills_score"]) / 100,
        experience_score=float(explanation_data["experience_score"]) / 100,
        semantic_score=float(explanation_data["semantic_score"]) / 100,
        education_score=float(explanation_data["education_score"]) / 100,
        location_score=float(explanation_data["location_score"]) / 100,
        availability_score=float(explanation_data["availability_score"]) / 100,
        matched_skills=list(explanation_data["matched_skills"]),
        missing_skills=list(explanation_data["missing_skills"]),
        global_score_before_penalty=float(
            explanation_data["global_score_before_penalty"]
        )
        / 100,
        penalty_factor=float(explanation_data["penalty_factor"]),
        explanation_data=explanation_data,
    )


def compatibility_rank_label(score: int) -> str:
    return classify_score(float(score))
