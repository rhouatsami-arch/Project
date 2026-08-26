from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_candidate
from app.database import get_db
from app.models.recruitment import (
    Application,
    ApplicationStatus,
    Job,
    JobStatus,
    SavedJob,
    Student,
)
from app.modules.matching.service import MatchingService
from app.modules.platform.audit import AuditAction, record_audit
from app.modules.users.service import UserService
from app.routers.cv_routes import build_cv_routes
from app.schemas.candidate import (
    Candidate,
    CandidateApplicationOut,
    CandidateDashboardApplicationOut,
    CandidateDashboardOut,
    CandidateSavedJobOut,
    CandidateUpdate,
)
from app.schemas.recruitment import ApplicationCreate

router = APIRouter(prefix="/candidates", tags=["candidates", "users"])


@router.get("/me", response_model=Candidate)
def get_profile(current: Student = Depends(get_current_candidate)):
    return current


@router.patch("/me", response_model=Candidate)
def update_profile(
    payload: CandidateUpdate,
    current: Student = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current, field, value)
    record_audit(
        db,
        actor_email=current.email,
        actor_role="candidate",
        action=AuditAction.UPDATE_PROFILE,
        resource=str(current.id),
    )
    db.commit()
    db.refresh(current)
    return current


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(
    current: Student = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    candidate_id = current.id
    email = current.email
    UserService.delete_student(current, db)
    record_audit(
        db,
        actor_email=email,
        actor_role="candidate",
        action=AuditAction.DELETE_PROFILE,
        resource=str(candidate_id),
    )
    db.commit()


@router.post(
    "/jobs/{job_id}/apply",
    response_model=CandidateApplicationOut,
    status_code=status.HTTP_201_CREATED,
)
def apply_to_job(
    job_id: int,
    payload: ApplicationCreate,
    current: Student = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.status == JobStatus.open).first()
    if not job:
        raise HTTPException(status_code=404, detail="Open job not found")

    application = Application(
        student_id=current.id,
        job_id=job.id,
        cover_letter=payload.cover_letter,
        match_score=MatchingService.compatibility_score(current, job),
    )
    db.add(application)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="You already applied to this job")
    db.refresh(application)
    record_audit(
        db,
        actor_email=current.email,
        actor_role="candidate",
        action=AuditAction.APPLY_JOB,
        resource=str(application.id),
        details=f"job:{job.id} · {job.title} · score:{application.match_score}",
    )
    db.commit()
    return application


@router.get("/me/applications", response_model=list[CandidateApplicationOut])
def my_applications(
    current: Student = Depends(get_current_candidate), db: Session = Depends(get_db)
):
    return (
        db.query(Application)
        .filter(Application.student_id == current.id)
        .order_by(Application.created_at.desc())
        .all()
    )


@router.get("/me/dashboard", response_model=CandidateDashboardOut)
def my_dashboard(
    current: Student = Depends(get_current_candidate), db: Session = Depends(get_db)
):
    applications = (
        db.query(Application)
        .options(joinedload(Application.job))
        .filter(Application.student_id == current.id)
        .order_by(Application.created_at.desc())
        .all()
    )
    saved_jobs = (
        db.query(SavedJob)
        .options(joinedload(SavedJob.job))
        .filter(SavedJob.student_id == current.id)
        .order_by(SavedJob.created_at.desc())
        .all()
    )

    dashboard_applications = [
        CandidateDashboardApplicationOut(
            id=application.id,
            job_id=application.job_id,
            job_title=application.job.title,
            job_location=application.job.location,
            job_employment_type=application.job.employment_type,
            cover_letter=application.cover_letter,
            internship_type=application.internship_type,
            status=application.status,
            match_score=application.match_score,
            interview_message=application.interview_message,
            interview_at=application.interview_at,
            created_at=application.created_at,
        )
        for application in applications
    ]

    return CandidateDashboardOut(
        total_applications=len(applications),
        interview_invites=sum(
            1
            for application in applications
            if application.status == ApplicationStatus.interview_invited
        ),
        saved_jobs_count=len(saved_jobs),
        applications=dashboard_applications,
        saved_jobs=saved_jobs,
    )


@router.post(
    "/jobs/{job_id}/save",
    response_model=CandidateSavedJobOut,
    status_code=status.HTTP_201_CREATED,
)
def save_job(
    job_id: int,
    current: Student = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.status == JobStatus.open).first()
    if not job:
        raise HTTPException(status_code=404, detail="Open job not found")

    saved = SavedJob(student_id=current.id, job_id=job.id)
    db.add(saved)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Job already saved")
    db.refresh(saved)
    return saved


@router.delete("/jobs/{job_id}/save", status_code=status.HTTP_204_NO_CONTENT)
def unsave_job(
    job_id: int,
    current: Student = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    saved = (
        db.query(SavedJob)
        .filter(SavedJob.student_id == current.id, SavedJob.job_id == job_id)
        .first()
    )
    if not saved:
        raise HTTPException(status_code=404, detail="Saved job not found")
    db.delete(saved)
    db.commit()


@router.get("/me/saved-jobs", response_model=list[CandidateSavedJobOut])
def my_saved_jobs(
    current: Student = Depends(get_current_candidate), db: Session = Depends(get_db)
):
    return (
        db.query(SavedJob)
        .filter(SavedJob.student_id == current.id)
        .order_by(SavedJob.created_at.desc())
        .all()
    )


build_cv_routes(router, get_current_candidate)
