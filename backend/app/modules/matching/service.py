from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.models.platform import RecommendationHistory
from app.models.recruitment import Application, Job, JobStatus, Student
from app.modules.matching.pipeline import MatchingPipeline, MatchResult
from app.modules.matching.scorer import ApplicantProfile, JobProfile

logger = logging.getLogger(__name__)


class MatchingService:
    @staticmethod
    def profile_from_student(student: Student) -> ApplicantProfile:
        location_hint = " · ".join(
            part for part in [student.university, student.bio] if part and part.strip()
        )
        return ApplicantProfile(
            technical_skills=student.technical_skills,
            soft_skills=student.soft_skills,
            skills=student.skills,
            cv_extracted_text=student.cv_extracted_text,
            field_of_study=student.field_of_study,
            experiences=student.experiences,
            projects=student.projects,
            bio=student.bio,
            certifications=student.certifications,
            languages=student.languages,
            internship_type=student.internship_type,
            location=location_hint or None,
        )

    @staticmethod
    def profile_from_job(job: Job) -> JobProfile:
        return JobProfile(
            title=job.title,
            description=job.description,
            required_skills=job.required_skills,
            location=job.location,
            employment_type=job.employment_type,
            remote_policy=job.employment_type,
            required_experience=job.description,
            required_education=job.description,
        )

    @classmethod
    def score_student_job(cls, student: Student, job: Job) -> MatchResult:
        try:
            return MatchingPipeline.run(
                cls.profile_from_student(student), cls.profile_from_job(job)
            )
        except Exception as exc:
            logger.warning(
                "Matching failed for student=%s job=%s: %s",
                student.id,
                job.id,
                exc,
            )
            raise

    @classmethod
    def safe_score_student_job(cls, student: Student, job: Job) -> MatchResult | None:
        """Score without failing the whole batch when one pair is invalid."""
        try:
            return cls.score_student_job(student, job)
        except Exception as exc:
            logger.warning(
                "Skipping job %s for student %s: %s",
                job.id,
                student.id,
                exc,
            )
            return None

    @classmethod
    def compatibility_score(cls, student: Student, job: Job) -> int:
        return cls.score_student_job(student, job).compatibility_score

    @classmethod
    def recommend_jobs(
        cls,
        db: Session,
        student: Student,
        *,
        limit: int = 10,
        min_score: int = 0,
    ) -> list[tuple[Job, MatchResult]]:
        jobs = (
            db.query(Job)
            .filter(Job.status == JobStatus.open)
            .order_by(Job.created_at.desc())
            .all()
        )
        ranked: list[tuple[Job, MatchResult]] = []
        for job in jobs:
            result = cls.safe_score_student_job(student, job)
            if result is None:
                continue
            if result.compatibility_score >= min_score:
                ranked.append((job, result))
        ranked.sort(key=lambda item: item[1].compatibility_score, reverse=True)
        return ranked[:limit]

    @classmethod
    def record_recommendations(
        cls,
        db: Session,
        student: Student,
        ranked: list[tuple[Job, object]],
    ) -> None:
        for job, result in ranked:
            db.add(
                RecommendationHistory(
                    student_id=student.id,
                    job_id=job.id,
                    compatibility_score=result.compatibility_score,
                    explanation=result.explanation,
                )
            )

    @classmethod
    def rank_applications(
        cls,
        applications: list[Application],
        job: Job,
        *,
        min_score: int = 0,
    ) -> list[tuple[Application, MatchResult]]:
        ranked: list[tuple[Application, MatchResult]] = []
        for application in applications:
            if not application.student:
                logger.warning("Application %s has no student profile", application.id)
                continue
            result = cls.safe_score_student_job(application.student, job)
            if result is None:
                continue
            if result.compatibility_score >= min_score:
                ranked.append((application, result))
        ranked.sort(key=lambda item: item[1].compatibility_score, reverse=True)
        return ranked
