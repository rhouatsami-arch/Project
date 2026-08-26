"""Service-level tests — job recommendations and candidate ranking."""

from app.auth import hash_password
from app.models.recruitment import Application, Job, JobStatus, Recruiter, Student
from app.modules.matching.service import MatchingService


def test_recommend_jobs_ranks_by_score(db_session, sample_student, sample_job):
    recruiter = db_session.get(Recruiter, sample_job.recruiter_id)
    low_match_job = Job(
        recruiter_id=recruiter.id,
        title="Java Enterprise Architect",
        description="10 years Java Spring required.",
        required_skills="java,spring,hibernate",
        location="Lyon",
        status=JobStatus.open,
    )
    db_session.add(low_match_job)
    db_session.commit()

    ranked = MatchingService.recommend_jobs(
        db_session, sample_student, limit=10, min_score=0
    )

    assert len(ranked) == 2
    scores = [result.compatibility_score for _, result in ranked]
    assert scores == sorted(scores, reverse=True)
    assert ranked[0][0].title == "Backend Developer"


def test_recommend_jobs_respects_min_score(db_session, sample_student, sample_job):
    ranked = MatchingService.recommend_jobs(
        db_session, sample_student, limit=10, min_score=99
    )
    assert ranked == []


def test_rank_applications(db_session, sample_student, sample_job):
    weak_student = Student(
        email="weak@test.com",
        hashed_password=hash_password("Password123"),
        first_name="Weak",
        last_name="Profile",
        technical_skills="java",
        account_kind="student",
    )
    db_session.add(weak_student)
    db_session.commit()
    db_session.refresh(weak_student)

    app_strong = Application(student_id=sample_student.id, job_id=sample_job.id)
    app_weak = Application(student_id=weak_student.id, job_id=sample_job.id)
    db_session.add_all([app_strong, app_weak])
    db_session.commit()

    ranked = MatchingService.rank_applications(
        [app_strong, app_weak], sample_job, min_score=0
    )

    assert len(ranked) == 2
    assert ranked[0][0].student_id == sample_student.id
    assert ranked[0][1].compatibility_score >= ranked[1][1].compatibility_score


def test_safe_score_returns_none_on_pipeline_error(
    monkeypatch, sample_student, sample_job
):
    def boom(*_args, **_kwargs):
        raise RuntimeError("pipeline failure")

    monkeypatch.setattr("app.modules.matching.service.MatchingPipeline.run", boom)
    result = MatchingService.safe_score_student_job(sample_student, sample_job)
    assert result is None
