from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_recruiter
from app.database import get_db
from app.models.recruitment import Application, ApplicationStatus, Job, Recruiter, Student
from app.schemas.recruitment import CandidateOut, InterviewInvite, RecruiterOut, RecruiterUpdate
from app.services.recruitment import candidate_match_score, send_interview_email

router = APIRouter(prefix="/recruiters", tags=["recruiters"])


@router.get("/me", response_model=RecruiterOut)
def get_profile(current: Recruiter = Depends(get_current_recruiter)):
    return current


@router.patch("/me", response_model=RecruiterOut)
def update_profile(
    payload: RecruiterUpdate,
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current, field, value)
    db.commit()
    db.refresh(current)
    return current


@router.get("/jobs/{job_id}/candidates", response_model=list[CandidateOut])
def list_candidates_for_job(
    job_id: int,
    min_score: int = 0,
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    applications = (
        db.query(Application)
        .options(joinedload(Application.student))
        .filter(Application.job_id == job.id)
        .all()
    )
    candidates = []
    for application in applications:
        score = candidate_match_score(application.student.technical_skills or application.student.skills, job.required_skills)
        if application.match_score != score:
            application.match_score = score
        if score >= min_score:
            candidates.append(_candidate_out(application, score))
    db.commit()
    return sorted(candidates, key=lambda candidate: candidate.match_score, reverse=True)


@router.post("/applications/{application_id}/shortlist", response_model=CandidateOut)
def shortlist_candidate(
    application_id: int,
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    application = _owned_application(application_id, current.id, db)
    application.status = ApplicationStatus.shortlisted
    application.match_score = candidate_match_score(application.student.technical_skills or application.student.skills, application.job.required_skills)
    db.commit()
    db.refresh(application)
    return _candidate_out(application, application.match_score)


@router.post("/applications/{application_id}/invite", response_model=CandidateOut)
def invite_candidate(
    application_id: int,
    payload: InterviewInvite,
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    application = _owned_application(application_id, current.id, db)
    message = payload.message or (
        f"Hello {application.student.first_name},\n\n"
        f"{current.company_name} would like to invite you for an interview for {application.job.title} "
        f"on {payload.interview_at.isoformat()}.\n\n"
        "Best regards"
    )

    send_interview_email(
        to_email=application.student.email,
        subject=f"Interview invitation for {application.job.title}",
        body=message,
    )
    application.status = ApplicationStatus.interview_invited
    application.interview_at = payload.interview_at
    application.interview_message = message
    application.match_score = candidate_match_score(application.student.technical_skills or application.student.skills, application.job.required_skills)
    db.commit()
    db.refresh(application)
    return _candidate_out(application, application.match_score)


def _owned_application(application_id, recruiter_id, db: Session) -> Application:
    application = (
        db.query(Application)
        .options(joinedload(Application.student), joinedload(Application.job))
        .join(Job)
        .filter(Application.id == application_id, Job.recruiter_id == recruiter_id)
        .first()
    )
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


def _candidate_out(application: Application, score: int) -> CandidateOut:
    student: Student = application.student
    return CandidateOut(
        application_id=application.id,
        student_id=student.id,
        full_name=f"{student.first_name} {student.last_name}",
        email=student.email,
        phone=student.phone,
        university=student.university,
        field_of_study=student.field_of_study,
        skills=student.skills,
        technical_skills=student.technical_skills,
        soft_skills=student.soft_skills,
        experiences=student.experiences,
        projects=student.projects,
        certifications=student.certifications,
        languages=student.languages,
        cv_filename=student.cv_filename,
        application_status=application.status,
        match_score=score,
    )
