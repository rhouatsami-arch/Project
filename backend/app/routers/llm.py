from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_candidate, get_current_recruiter, get_current_student
from app.database import get_db
from app.models.platform import Notification, RecommendationHistory
from app.models.recruitment import Application, Job, Recruiter, Student
from app.modules.llm.service import LlmInsight, LlmService
from app.modules.matching.service import MatchingService
from app.schemas.matching import (
    CvSummaryOut,
    LlmExplanationOut,
    LlmModuleInfoOut,
    MatchScoreRequest,
)

router = APIRouter(prefix="/llm", tags=["llm", "ai-explanation"])


@router.get("/module", response_model=LlmModuleInfoOut)
def llm_module_info():
    return LlmModuleInfoOut(**LlmService.module_info())


@router.post("/explain", response_model=LlmExplanationOut)
def explain_match(payload: MatchScoreRequest):
    profile = _profile_from_request(payload)
    job = _job_from_request(payload)
    return _insight_out(LlmService.analyze(profile, job))


@router.get("/candidates/me/cv-summary", response_model=CvSummaryOut)
def candidate_cv_summary(current: Student = Depends(get_current_candidate)):
    profile = MatchingService.profile_from_student(current)
    return CvSummaryOut(summary=LlmService.cv_summary_only(profile))


@router.get("/students/me/cv-summary", response_model=CvSummaryOut)
def student_cv_summary(current: Student = Depends(get_current_student)):
    profile = MatchingService.profile_from_student(current)
    return CvSummaryOut(summary=LlmService.cv_summary_only(profile))


@router.get("/candidates/me/explain-job/{job_id}", response_model=LlmExplanationOut)
def explain_job_for_candidate(
    job_id: int,
    current: Student = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    return _explain_job(db, current, job_id)


@router.get("/students/me/explain-job/{job_id}", response_model=LlmExplanationOut)
def explain_job_for_student(
    job_id: int,
    current: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    return _explain_job(db, current, job_id)


@router.get(
    "/recruiters/applications/{application_id}/explain",
    response_model=LlmExplanationOut,
)
def explain_application_for_recruiter(
    application_id: int,
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    application = (
        db.query(Application)
        .options(joinedload(Application.student), joinedload(Application.job))
        .join(Job)
        .filter(
            Application.id == application_id,
            Job.recruiter_id == current.id,
        )
        .first()
    )
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    insight = LlmService.analyze(
        MatchingService.profile_from_student(application.student),
        MatchingService.profile_from_job(application.job),
    )
    return _insight_out(insight)


@router.get("/candidates/me/notifications")
def candidate_notifications(
    current: Student = Depends(get_current_candidate), db: Session = Depends(get_db)
):
    return _notifications(db, current.email)


@router.get("/students/me/notifications")
def student_notifications(
    current: Student = Depends(get_current_student), db: Session = Depends(get_db)
):
    return _notifications(db, current.email)


@router.get("/recruiters/me/notifications")
def recruiter_notifications(
    current: Recruiter = Depends(get_current_recruiter), db: Session = Depends(get_db)
):
    return _notifications(db, current.email)


@router.get("/candidates/me/recommendation-history")
def candidate_history(
    current: Student = Depends(get_current_candidate), db: Session = Depends(get_db)
):
    return _history(db, current)


@router.get("/students/me/recommendation-history")
def student_history(
    current: Student = Depends(get_current_student), db: Session = Depends(get_db)
):
    return _history(db, current)


def _explain_job(db: Session, student: Student, job_id: int) -> LlmExplanationOut:
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    insight = LlmService.analyze(
        MatchingService.profile_from_student(student),
        MatchingService.profile_from_job(job),
    )
    return _insight_out(insight)


def _insight_out(insight: LlmInsight) -> LlmExplanationOut:
    return LlmExplanationOut(
        compatibility_score=insight.compatibility_score,
        rank_label=insight.rank_label,
        explanation=insight.explanation,
        cv_summary=insight.cv_summary,
        job_summary=insight.job_summary,
        matched_skills=insight.matched_skills,
        missing_skills=insight.missing_skills,
        strengths=insight.strengths,
        score_justification=insight.score_justification,
        improvement_tips=insight.improvement_tips,
        interview_questions=insight.interview_questions,
        disclaimer=insight.disclaimer,
        confidence_score=insight.confidence_score,
        grounded=insight.grounded,
        guard_warnings=insight.guard_warnings,
        grounded_sources=insight.grounded_sources,
    )


def _profile_from_request(payload: MatchScoreRequest):
    from app.modules.matching.scorer import ApplicantProfile

    return ApplicantProfile(
        technical_skills=payload.technical_skills,
        soft_skills=payload.soft_skills,
        skills=payload.skills,
        cv_extracted_text=payload.cv_extracted_text,
        field_of_study=payload.field_of_study,
        experiences=payload.experiences,
        projects=payload.projects,
        bio=payload.bio,
        internship_type=payload.internship_type,
        location=payload.location,
    )


def _job_from_request(payload: MatchScoreRequest):
    from app.modules.matching.scorer import JobProfile

    return JobProfile(
        title=payload.job_title,
        description=payload.job_description,
        required_skills=payload.required_skills,
        location=payload.job_location,
        employment_type=payload.employment_type,
    )


def _notifications(db: Session, email: str):
    items = (
        db.query(Notification)
        .filter(Notification.user_email == email)
        .order_by(Notification.created_at.desc())
        .limit(20)
        .all()
    )
    return [
        {
            "id": n.id,
            "type": n.type.value,
            "title": n.title,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat(),
        }
        for n in items
    ]


def _history(db: Session, student: Student):
    items = (
        db.query(RecommendationHistory)
        .filter(RecommendationHistory.student_id == student.id)
        .order_by(RecommendationHistory.created_at.desc())
        .limit(20)
        .all()
    )
    return [
        {
            "id": h.id,
            "job_id": h.job_id,
            "compatibility_score": h.compatibility_score,
            "explanation": h.explanation,
            "created_at": h.created_at.isoformat(),
        }
        for h in items
    ]
