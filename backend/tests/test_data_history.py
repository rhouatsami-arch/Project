"""Tests — historique des recommandations (couche données)."""

from app.models.platform import RecommendationHistory
from app.modules.matching.service import MatchingService


def test_record_recommendations_persists_history(
    db_session, sample_student, sample_job
):
    ranked = MatchingService.recommend_jobs(
        db_session, sample_student, limit=5, min_score=0
    )
    assert ranked

    MatchingService.record_recommendations(db_session, sample_student, ranked)
    db_session.commit()

    rows = (
        db_session.query(RecommendationHistory)
        .filter(RecommendationHistory.student_id == sample_student.id)
        .all()
    )
    assert len(rows) >= 1
    row = rows[0]
    assert row.job_id == sample_job.id
    assert 0 <= row.compatibility_score <= 100
    assert row.explanation
    assert row.created_at is not None


def test_recommendation_history_linked_to_student_and_job(
    db_session, sample_student, sample_job
):
    ranked = MatchingService.recommend_jobs(db_session, sample_student, limit=1)
    MatchingService.record_recommendations(db_session, sample_student, ranked)
    db_session.commit()

    history = db_session.query(RecommendationHistory).first()
    assert history.student_id == sample_student.id
    assert history.job_id in {job.id for job, _ in ranked}
