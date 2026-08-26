"""Unit tests for matching score formula and NLP helpers."""

import pytest

from app.modules.matching.matching_score_service import (
    MatchingCandidate,
    MatchingJob,
    calculate_matching_score,
)
from app.modules.matching.nlp import split_skill_tokens, tfidf_cosine_similarity
from app.modules.matching.score_formula import (
    classify_score,
    compute_penalties,
    compute_skills_score,
    extract_experience_years,
    parse_required_optional_skills,
)


def test_parse_required_optional_skills():
    required, optional = parse_required_optional_skills(
        "python,sql,fastapi|optional:docker,aws"
    )
    assert required == {"python", "sql", "fastapi"}
    assert optional == {"docker", "aws"}


def test_split_skill_tokens_handles_empty():
    assert split_skill_tokens(None) == set()
    assert split_skill_tokens("") == set()


def test_extract_experience_years_from_text():
    assert extract_experience_years("3 ans d'expérience en Python") == 3.0
    assert extract_experience_years("no experience mentioned") is None


def test_compute_skills_score_full_match():
    score, matched, missing, _, _ = compute_skills_score(
        {"python", "sql", "docker"},
        {"python", "sql"},
        {"docker"},
    )
    assert score == 1.0
    assert matched == ["python", "sql"]
    assert missing == []


def test_compute_skills_score_partial_match():
    score, _, missing, _, _ = compute_skills_score(
        {"python"},
        {"python", "sql", "fastapi"},
        set(),
    )
    assert score < 1.0
    assert "sql" in missing
    assert "fastapi" in missing


def test_classify_score_labels():
    assert classify_score(90) == "Très forte compatibilité"
    assert classify_score(75) == "Bonne compatibilité"
    assert classify_score(30) == "Profil non recommandé"


def test_compute_penalties_applies_critical_skill_penalty():
    factor, applied = compute_penalties(
        missing_required=["python"],
        experience_score=0.8,
        cv_complete=True,
        location_score=1.0,
        availability_score=1.0,
        on_site_job=False,
    )
    assert factor < 1.0
    assert applied


def test_tfidf_cosine_similarity_empty_inputs():
    assert tfidf_cosine_similarity(None, "job description") == 0.0
    assert tfidf_cosine_similarity("cv text", None) == 0.0


def test_calculate_matching_score_strong_candidate():
    candidate = MatchingCandidate(
        skills={"python", "sql", "fastapi", "docker"},
        experience_years=3.0,
        resume_text="Python developer with FastAPI and PostgreSQL experience.",
        education="Computer Science",
        location="Paris",
        availability="immediate",
        cv_complete=True,
    )
    job = MatchingJob(
        required_skills={"python", "fastapi"},
        optional_skills={"docker"},
        required_experience=2.0,
        description="Backend developer Python FastAPI API REST",
        required_education="Computer Science",
        location="Paris",
        remote_policy="hybrid",
    )

    final_score, explanation = calculate_matching_score(candidate, job)

    assert 0.0 <= final_score <= 1.0
    assert explanation["global_score"] >= 50
    assert "python" in explanation["matched_skills"]


def test_calculate_matching_score_rejects_none_inputs():
    with pytest.raises(ValueError, match="candidate and job are required"):
        calculate_matching_score(None, MatchingJob())  # type: ignore[arg-type]
