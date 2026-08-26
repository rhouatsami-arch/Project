"""Tests for LLM anti-hallucination guard."""

from app.modules.llm.guard import HallucinationGuard
from app.modules.llm.service import LlmService
from app.modules.matching.scorer import ApplicantProfile, JobProfile


def _profile(**kwargs) -> ApplicantProfile:
    defaults = {
        "technical_skills": "python, fastapi, sql",
        "soft_skills": "communication",
        "experiences": "Stage backend chez Acme",
        "projects": "API REST MatiousHire",
        "field_of_study": "Informatique",
    }
    defaults.update(kwargs)
    return ApplicantProfile(**defaults)


def _job(**kwargs) -> JobProfile:
    defaults = {
        "title": "Développeur Python",
        "description": "Backend FastAPI et PostgreSQL",
        "required_skills": "python, fastapi, postgresql",
        "location": "Paris",
    }
    defaults.update(kwargs)
    return JobProfile(**defaults)


def test_guard_architecture_has_layers():
    arch = HallucinationGuard.architecture()
    assert arch["strategy"] == "grounded_hybrid"
    assert len(arch["layers"]) == 4
    assert "principles" in arch


def test_llm_insight_includes_confidence_and_sources():
    insight = LlmService.analyze(_profile(), _job())
    assert 0 <= insight.confidence_score <= 100
    assert isinstance(insight.grounded, bool)
    assert isinstance(insight.guard_warnings, list)
    assert len(insight.grounded_sources) > 0
    assert "score:skills_score" in insight.grounded_sources


def test_guard_softens_speculative_language():
    from app.modules.matching.scorer import compute_compatibility_score

    profile = _profile()
    job = _job()
    breakdown = compute_compatibility_score(profile, job)
    guard = HallucinationGuard.apply(
        profile=profile,
        job=job,
        breakdown=breakdown,
        explanation="Ce candidat est certainement le meilleur candidat du marché.",
        cv_summary="Profil python.",
        strengths=["Maîtrise de compétences clés : python"],
    )
    assert "certainement" not in guard.sanitized_explanation.lower()
    assert any("spéculatif" in w.lower() for w in guard.guard_warnings)


def test_guard_low_confidence_on_sparse_profile():
    insight = LlmService.analyze(
        _profile(experiences="", projects="", technical_skills=""),
        _job(),
    )
    assert insight.confidence_score < 80
    assert insight.guard_warnings or "limitée" in insight.explanation
