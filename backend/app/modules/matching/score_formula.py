"""
Score de matching CV-offre — méthode hybride explicable (PFE MatiousHire).

Formule globale (doc. §3.1) :
    S_global = 0.35·S_comp + 0.25·S_exp + 0.20·S_sem + 0.10·S_form
               + 0.05·S_loc + 0.05·S_disp

Compétences (doc. §3.2) :
    S_comp = 0.70·S_obligatoires + 0.30·S_souhaitées

Expérience (doc. §3.3) :
    S_exp = min(Exp_candidat / Exp_requise, 1) + bonus_domaine

Pénalités (doc. §4.1) appliquées multiplicativement sur S_global.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.modules.matching.nlp import (
    jaccard_similarity,
    split_skill_tokens,
    tfidf_cosine_similarity,
)

# --- Pondérations globales (Table 3.1) ---
SCORE_WEIGHTS: dict[str, float] = {
    "skills": 0.35,
    "experience": 0.25,
    "semantic": 0.20,
    "education": 0.10,
    "location": 0.05,
    "availability": 0.05,
}

MANDATORY_SKILLS_WEIGHT = 0.70
OPTIONAL_SKILLS_WEIGHT = 0.30

EXPERIENCE_DOMAIN_BONUS = 0.10
EXPERIENCE_CLOSE_BONUS = 0.05

PENALTY_CRITICAL_SKILL = 0.75
PENALTY_LOW_EXPERIENCE = 0.80
PENALTY_INCOMPLETE_CV = 0.90
PENALTY_LOCATION = 0.70
PENALTY_AVAILABILITY = 0.80

YEAR_PATTERN = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(?:ans?(?:\s+d['']?exp(?:érience)?)?|years?|yr\b)",
    re.IGNORECASE,
)
OPTIONAL_SKILLS_SPLIT = re.compile(r"\|\s*optional\s*:|;\s*optional\s*:", re.IGNORECASE)
REMOTE_KEYWORDS = {"remote", "télétravail", "teletravail", "hybrid", "hybride"}

FEEDBACK_VALUES: dict[str, float] = {
    "very_relevant": 1.00,
    "relevant": 0.75,
    "average": 0.50,
    "low": 0.25,
    "not_relevant": 0.00,
}


@dataclass(frozen=True)
class MatchingScoreResult:
    """Résultat aligné sur le pseudo-code doc. §10.1."""

    final_score: float
    global_score: float
    penalty_factor: float
    skills_score: float
    experience_score: float
    semantic_score: float
    education_score: float
    location_score: float
    availability_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    matched_optional_skills: list[str]
    missing_optional_skills: list[str]
    penalties_applied: list[str]
    rank_label: str
    explanation_data: dict[str, object]


def parse_required_optional_skills(raw: str | None) -> tuple[set[str], set[str]]:
    """
    Sépare compétences obligatoires et souhaitées.

    Formats acceptés :
    - ``python,sql|optional:docker,aws``
    - ``python,sql;optional:docker,aws``
    - ``python,sql|docker,aws`` (segment après | = souhaitées)
    """
    if not raw:
        return set(), set()

    text = raw.strip()
    for pattern in (r"\|\s*optional\s*:", r";\s*optional\s*:"):
        if re.search(pattern, text, re.IGNORECASE):
            required_part, optional_part = re.split(
                pattern, text, maxsplit=1, flags=re.IGNORECASE
            )
            return split_skill_tokens(required_part), split_skill_tokens(optional_part)

    if "|" in text:
        required_part, optional_part = text.split("|", 1)
        return split_skill_tokens(required_part), split_skill_tokens(optional_part)

    return split_skill_tokens(text), set()


def extract_experience_years(text: str | None) -> float | None:
    if not text:
        return None
    try:
        values = (
            float(value.replace(",", "."))
            for value in YEAR_PATTERN.findall(text)
        )
        return max(values)
    except ValueError:
        return None


def compute_skills_score(
    candidate_skills: set[str],
    required_skills: set[str],
    optional_skills: set[str],
) -> tuple[float, list[str], list[str], list[str], list[str]]:
    """Doc. §3.2 — S_comp = 0.70·S_obligatoires + 0.30·S_souhaitées."""
    if not required_skills and not optional_skills:
        return 0.0, [], [], [], []

    mandatory_ratio = 0.0
    matched_required: list[str] = []
    missing_required: list[str] = []
    if required_skills:
        matched_required = sorted(required_skills & candidate_skills)
        missing_required = sorted(required_skills - candidate_skills)
        mandatory_ratio = len(matched_required) / len(required_skills)

    optional_ratio = 0.0
    matched_optional: list[str] = []
    missing_optional: list[str] = []
    if optional_skills:
        matched_optional = sorted(optional_skills & candidate_skills)
        missing_optional = sorted(optional_skills - candidate_skills)
        optional_ratio = len(matched_optional) / len(optional_skills)
    elif required_skills:
        optional_ratio = mandatory_ratio

    if required_skills and optional_skills:
        score = (MANDATORY_SKILLS_WEIGHT * mandatory_ratio) + (
            OPTIONAL_SKILLS_WEIGHT * optional_ratio
        )
    elif required_skills:
        score = mandatory_ratio
    else:
        score = optional_ratio

    return (
        min(score, 1.0),
        matched_required,
        missing_required,
        matched_optional,
        missing_optional,
    )


def compute_experience_score(
    candidate_years: float | None,
    required_years: float | None,
    *,
    same_domain: bool = False,
    close_domain: bool = False,
) -> float:
    """Doc. §3.3 — ratio plafonné à 1 + bonus qualitatif."""
    if required_years and required_years > 0 and candidate_years is not None:
        base = min(candidate_years / required_years, 1.0)
    elif candidate_years:
        base = min(candidate_years / 3.0, 1.0)
    else:
        base = 0.0

    bonus = 0.0
    if same_domain:
        bonus = EXPERIENCE_DOMAIN_BONUS
    elif close_domain:
        bonus = EXPERIENCE_CLOSE_BONUS

    return min(base + bonus, 1.0)


def compute_semantic_similarity(
    resume_text: str | None, job_description: str | None
) -> float:
    """Doc. §3.4 — similarité cosinus TF-IDF."""
    return min(tfidf_cosine_similarity(resume_text, job_description), 1.0)


def compute_education_score(
    candidate_education: str | None,
    required_education_hint: str | None,
) -> float:
    """Doc. §3.5 — grille qualitative."""
    education = (candidate_education or "").strip().lower()
    required = (required_education_hint or "").strip().lower()

    if not education:
        return 0.30
    if not required:
        return 0.50

    if education in required or required in education:
        return 1.00

    overlap = jaccard_similarity(set(education.split()), set(required.split()))
    if overlap >= 0.35:
        return 0.75
    if overlap >= 0.15:
        return 0.50
    return 0.20


def compute_location_score(
    candidate_location: str | None,
    job_location: str | None,
    *,
    remote_policy: str | None = None,
) -> float:
    """Doc. §3.6 / Table 3.4."""
    job_loc = (job_location or "").strip().lower()
    candidate_loc = (candidate_location or "").strip().lower()
    remote = (remote_policy or "").strip().lower()

    if any(keyword in job_loc or keyword in remote for keyword in REMOTE_KEYWORDS):
        return 1.00
    if not job_loc:
        return 0.75
    if not candidate_loc:
        return 0.40

    if job_loc in candidate_loc or candidate_loc in job_loc:
        return 1.00

    job_tokens = set(job_loc.replace(",", " ").split())
    candidate_tokens = set(candidate_loc.replace(",", " ").split())
    if job_tokens & candidate_tokens:
        return 0.75

    mobility_markers = {"mobil", "reloc", "déplac", "deplac", "flexible"}
    if any(marker in candidate_loc for marker in mobility_markers):
        return 0.50

    return 0.0


def compute_availability_score(
    candidate_availability: str | None,
    job_start_hint: str | None = None,
) -> float:
    """Doc. §3.6 / Table 3.5."""
    availability = (candidate_availability or "").strip().lower()
    start_hint = (job_start_hint or "").strip().lower()

    if not availability and not start_hint:
        return 0.40

    immediate = {
        "immédiat",
        "immediate",
        "disponible",
        "asap",
        "now",
        "dès que possible",
    }
    one_month = {"1 mois", "un mois", "sous un mois", "within a month"}
    later = {"2 mois", "3 mois", "deux mois", "trois mois", "semestre"}
    unavailable = {"indisponible", "non disponible", "not available", "unavailable"}

    text = f"{availability} {start_hint}"
    if any(term in text for term in unavailable):
        return 0.00
    if any(term in text for term in immediate):
        return 1.00
    if any(term in text for term in one_month):
        return 0.75
    if any(term in text for term in later):
        return 0.50
    if availability:
        return 0.75
    return 0.40


def compute_penalties(
    *,
    missing_required: list[str],
    experience_score: float,
    cv_complete: bool,
    location_score: float,
    availability_score: float,
    on_site_job: bool,
) -> tuple[float, list[str]]:
    """Doc. §4.1 — pénalités multiplicatives."""
    factor = 1.0
    applied: list[str] = []

    if missing_required:
        factor *= PENALTY_CRITICAL_SKILL
        missing_label = ", ".join(missing_required[:3])
        applied.append(
            f"compétence obligatoire critique absente ({missing_label}) "
            f"×{PENALTY_CRITICAL_SKILL}"
        )

    if experience_score < 0.40:
        factor *= PENALTY_LOW_EXPERIENCE
        applied.append(
            f"expérience très inférieure au minimum ×{PENALTY_LOW_EXPERIENCE}"
        )

    if not cv_complete:
        factor *= PENALTY_INCOMPLETE_CV
        applied.append(
            f"CV incomplet ou extraction incertaine ×{PENALTY_INCOMPLETE_CV}"
        )

    if on_site_job and location_score <= 0.0:
        factor *= PENALTY_LOCATION
        applied.append(
            f"localisation incompatible (poste présentiel) ×{PENALTY_LOCATION}"
        )

    if availability_score <= 0.0:
        factor *= PENALTY_AVAILABILITY
        applied.append(f"disponibilité incompatible ×{PENALTY_AVAILABILITY}")

    return factor, applied


def classify_score(score_percent: float) -> str:
    """Doc. §4.2 — interprétation du score final."""
    if score_percent >= 85:
        return "Très forte compatibilité"
    if score_percent >= 70:
        return "Bonne compatibilité"
    if score_percent >= 55:
        return "Compatibilité moyenne"
    if score_percent >= 40:
        return "Compatibilité faible"
    return "Profil non recommandé"


def recruiter_feedback_value(label: str) -> float:
    """Doc. §6.2 — conversion du feedback recruteur."""
    return FEEDBACK_VALUES.get(label.strip().lower(), 0.50)


def compute_feedback_error(recruiter_feedback: float, global_score: float) -> float:
    """Doc. §6.2 — Erreur = Feedback_recruteur − S_global."""
    return recruiter_feedback - global_score


def adjust_weight(
    old_weight: float,
    error: float,
    criterion_contribution: float,
    *,
    alpha: float = 0.05,
) -> float:
    """Doc. §6.3 — ajustement progressif des pondérations."""
    return max(0.0, old_weight + alpha * error * criterion_contribution)


def precision_at_k(relevant_ids: set[int], ranked_ids: list[int], k: int) -> float:
    """Doc. §8.1 — Précision@K."""
    if k <= 0:
        return 0.0
    top_k = ranked_ids[:k]
    if not top_k:
        return 0.0
    hits = sum(item_id in relevant_ids for item_id in top_k)
    return hits / len(top_k)


def calculate_matching_score(
    *,
    candidate_skills: set[str],
    candidate_experience_text: str | None,
    candidate_education: str | None,
    candidate_location: str | None,
    candidate_availability: str | None,
    resume_text: str | None,
    cv_complete: bool,
    job_required_skills: str | None,
    job_description: str | None,
    job_location: str | None = None,
    job_remote_policy: str | None = None,
    job_start_hint: str | None = None,
    job_required_experience: str | None = None,
) -> MatchingScoreResult:
    """
    Pseudo-code doc. §10.1 — calcule le score final et les données d'explication.
    """
    required, optional = parse_required_optional_skills(job_required_skills)
    (
        skills_score,
        matched_skills,
        missing_skills,
        matched_optional,
        missing_optional,
    ) = compute_skills_score(candidate_skills, required, optional)

    candidate_years = extract_experience_years(candidate_experience_text)
    required_years = extract_experience_years(
        job_required_experience or job_description
    )
    domain_text = " ".join(
        part
        for part in (candidate_experience_text or "", candidate_education or "")
        if part
    ).lower()
    job_text = (job_description or "").lower()
    if domain_text and job_text:
        similarity = jaccard_similarity(set(domain_text.split()), set(job_text.split()))
        same_domain = similarity >= 0.12
        close_domain = not same_domain and similarity >= 0.06
    else:
        same_domain = False
        close_domain = False
    experience_score = compute_experience_score(
        candidate_years,
        required_years,
        same_domain=same_domain,
        close_domain=close_domain,
    )

    semantic_score = compute_semantic_similarity(resume_text, job_description)
    education_score = compute_education_score(candidate_education, job_description)
    location_score = compute_location_score(
        candidate_location,
        job_location,
        remote_policy=job_remote_policy,
    )
    availability_score = compute_availability_score(
        candidate_availability,
        job_start_hint,
    )

    global_score = (
        SCORE_WEIGHTS["skills"] * skills_score
        + SCORE_WEIGHTS["experience"] * experience_score
        + SCORE_WEIGHTS["semantic"] * semantic_score
        + SCORE_WEIGHTS["education"] * education_score
        + SCORE_WEIGHTS["location"] * location_score
        + SCORE_WEIGHTS["availability"] * availability_score
    )

    job_loc_lower = (job_location or "").lower()
    job_remote_lower = (job_remote_policy or "").lower()
    on_site = not any(
        keyword in job_loc_lower or keyword in job_remote_lower
        for keyword in REMOTE_KEYWORDS
    )
    penalty_factor, penalties_applied = compute_penalties(
        missing_required=missing_skills,
        experience_score=experience_score,
        cv_complete=cv_complete,
        location_score=location_score,
        availability_score=availability_score,
        on_site_job=on_site,
    )
    final_score = min(max(global_score * penalty_factor, 0.0), 1.0)
    score_percent = round(final_score * 100)

    explanation_data = {
        "global_score": score_percent,
        "global_score_before_penalty": round(global_score * 100),
        "skills_score": round(skills_score * 100),
        "experience_score": round(experience_score * 100),
        "semantic_score": round(semantic_score * 100),
        "education_score": round(education_score * 100),
        "location_score": round(location_score * 100),
        "availability_score": round(availability_score * 100),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "matched_optional_skills": matched_optional,
        "missing_optional_skills": missing_optional,
        "experience_required_years": required_years,
        "experience_candidate_years": candidate_years,
        "penalty_factor": penalty_factor,
        "penalties_applied": penalties_applied,
        "formula": (
            "S_global = 0.35·S_comp + 0.25·S_exp + 0.20·S_sem + 0.10·S_form "
            "+ 0.05·S_loc + 0.05·S_disp ; S_final = S_global × pénalités"
        ),
    }

    return MatchingScoreResult(
        final_score=final_score,
        global_score=global_score,
        penalty_factor=penalty_factor,
        skills_score=skills_score,
        experience_score=experience_score,
        semantic_score=semantic_score,
        education_score=education_score,
        location_score=location_score,
        availability_score=availability_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        matched_optional_skills=matched_optional,
        missing_optional_skills=missing_optional,
        penalties_applied=penalties_applied,
        rank_label=classify_score(score_percent),
        explanation_data=explanation_data,
    )
