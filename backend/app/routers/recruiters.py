from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_recruiter
from app.database import get_db
from app.models.platform import Meeting, MeetingStatus, NotificationType
from app.models.recruitment import (
    Application,
    ApplicationStatus,
    Job,
    JobStatus,
    Recruiter,
    Student,
)
from app.modules.cv.service import CvService
from app.modules.matching.service import MatchingService
from app.modules.platform.audit import AuditAction, record_audit
from app.modules.platform.service import NotificationService
from app.modules.users.service import UserService
from app.schemas.candidate import CandidateOut, InterviewInvite
from app.schemas.cv import CvExtractedTextOut
from app.schemas.recruitment import (
    RecruiterDashboardOut,
    RecruiterOut,
    RecruiterRecentApplicationOut,
    RecruiterUpcomingMeetingOut,
    RecruiterUpdate,
)
from app.services.recruitment import (
    candidate_match_score_for_entities,
    send_interview_email,
)
from app.utils.datetime import utc_now

router = APIRouter(prefix="/recruiters", tags=["recruiters", "users"])


@router.get("/me", response_model=RecruiterOut)
def get_profile(current: Recruiter = Depends(get_current_recruiter)):
    return current


@router.get("/me/dashboard", response_model=RecruiterDashboardOut)
def recruiter_dashboard(
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    jobs = db.query(Job).filter(Job.recruiter_id == current.id).all()
    job_ids = [job.id for job in jobs]
    open_jobs = sum(job.status == JobStatus.open for job in jobs)
    closed_jobs = len(jobs) - open_jobs

    applications: list[Application] = []
    if job_ids:
        applications = (
            db.query(Application)
            .options(joinedload(Application.student), joinedload(Application.job))
            .filter(Application.job_id.in_(job_ids))
            .order_by(Application.created_at.desc())
            .all()
        )

    def count_status(value: ApplicationStatus) -> int:
        return sum(item.status == value for item in applications)

    # Include explicit zeros; consider None as missing
    scores = [item.match_score for item in applications if item.match_score is not None]
    average_match_score = int(round(sum(scores) / len(scores))) if scores else 0

    meetings = (
        db.query(Meeting)
        .filter(Meeting.recruiter_id == current.id)
        .order_by(Meeting.scheduled_at.asc())
        .all()
    )
    upcoming = [
        meeting
        for meeting in meetings
        if meeting.status
        in {MeetingStatus.proposed.value, MeetingStatus.accepted.value}
        and meeting.scheduled_at >= utc_now()
    ]

    recent_applications = []
    for application in applications[:8]:
        student = application.student
        recent_applications.append(
            RecruiterRecentApplicationOut(
                application_id=application.id,
                job_id=application.job_id,
                job_title=application.job.title if application.job else "Offre",
                candidate_name=f"{student.first_name} {student.last_name}",
                candidate_email=student.email,
                status=application.status.value
                if hasattr(application.status, "value")
                else str(application.status),
                match_score=application.match_score or 0,
                created_at=application.created_at.isoformat(),
            )
        )

    upcoming_meeting_list = []
    for meeting in upcoming[:6]:
        student = db.query(Student).filter(Student.id == meeting.student_id).first()
        candidate_name = (
            f"{student.first_name} {student.last_name}"
            if student
            else "Candidat"
        )
        status_val = getattr(meeting.status, "value", meeting.status)
        upcoming_meeting_list.append(
            RecruiterUpcomingMeetingOut(
                meeting_id=meeting.id,
                job_id=meeting.job_id,
                scheduled_at=meeting.scheduled_at.isoformat(),
                status=status_val,
                location=meeting.location,
                candidate_name=candidate_name,
            )
        )

    return RecruiterDashboardOut(
        open_jobs=open_jobs,
        closed_jobs=closed_jobs,
        total_applications=len(applications),
        applied_count=count_status(ApplicationStatus.applied),
        shortlisted_count=count_status(ApplicationStatus.shortlisted),
        interview_count=count_status(ApplicationStatus.interview_invited),
        rejected_count=count_status(ApplicationStatus.rejected),
        hired_count=count_status(ApplicationStatus.hired),
        upcoming_meetings=len(upcoming),
        average_match_score=average_match_score,
        recent_applications=recent_applications,
        upcoming_meeting_list=upcoming_meeting_list,
    )


@router.patch("/me", response_model=RecruiterOut)
def update_profile(
    payload: RecruiterUpdate,
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current, field, value)
    record_audit(
        db,
        actor_email=current.email,
        actor_role="recruiter",
        action=AuditAction.UPDATE_PROFILE,
        resource=str(current.id),
    )
    db.commit()
    db.refresh(current)
    return current


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    recruiter_id = current.id
    email = current.email
    UserService.delete_recruiter(current, db)
    record_audit(
        db,
        actor_email=email,
        actor_role="recruiter",
        action=AuditAction.DELETE_PROFILE,
        resource=str(recruiter_id),
    )
    db.commit()


@router.get("/jobs/{job_id}/candidates", response_model=list[CandidateOut])
def list_candidates_for_job(
    job_id: int,
    min_score: int = 0,
    status_filter: str | None = None,
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    query = (
        db.query(Application)
        .options(joinedload(Application.student))
        .filter(Application.job_id == job.id)
    )
    if status_filter:
        try:
            status_value = ApplicationStatus(status_filter)
        except ValueError as exc:
            raise HTTPException(
                status_code=400, detail="Invalid status_filter"
            ) from exc
        query = query.filter(Application.status == status_value)

    applications = query.all()
    ranked = MatchingService.rank_applications(applications, job, min_score=min_score)
    candidates = []
    for index, (application, result) in enumerate(ranked, start=1):
        application.match_score = result.compatibility_score
        candidates.append(
            _candidate_out(
                application,
                result.compatibility_score,
                rank=index,
                rank_label=result.rank_label,
                breakdown=result.breakdown,
                explanation=result.explanation,
            )
        )
    db.commit()
    return candidates


@router.post("/applications/{application_id}/shortlist", response_model=CandidateOut)
def shortlist_candidate(
    application_id: int,
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    application = _owned_application(application_id, current.id, db)
    application.status = ApplicationStatus.shortlisted
    application.match_score = candidate_match_score_for_entities(
        application.student, application.job
    )
    NotificationService.notify(
        db,
        user_email=application.student.email,
        user_role="candidate",
        type=NotificationType.system,
        title="Candidature shortlistée",
        message=(
            f"Votre candidature pour {application.job.title} a été shortlistée "
            f"par {current.company_name}."
        ),
        also_email=True,
        email_subject=f"Shortlist — {application.job.title}",
    )
    record_audit(
        db,
        actor_email=current.email,
        actor_role="recruiter",
        action=AuditAction.SHORTLIST_APPLICATION,
        resource=str(application.id),
        details=f"{application.student.email} · {application.job.title}",
    )
    db.commit()
    db.refresh(application)
    return _candidate_out(application, application.match_score)


@router.post("/applications/{application_id}/reject", response_model=CandidateOut)
def reject_candidate(
    application_id: int,
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    application = _owned_application(application_id, current.id, db)
    application.status = ApplicationStatus.rejected
    application.match_score = candidate_match_score_for_entities(
        application.student, application.job
    )
    NotificationService.notify(
        db,
        user_email=application.student.email,
        user_role="candidate",
        type=NotificationType.system,
        title="Candidature non retenue",
        message=(
            f"Votre candidature pour {application.job.title} n'a pas été retenue "
            f"pour le moment."
        ),
        also_email=True,
        email_subject=f"Retour candidature — {application.job.title}",
    )
    record_audit(
        db,
        actor_email=current.email,
        actor_role="recruiter",
        action=AuditAction.REJECT_APPLICATION,
        resource=str(application.id),
        details=f"{application.student.email} · {application.job.title}",
    )
    db.commit()
    db.refresh(application)
    return _candidate_out(application, application.match_score)


@router.post("/applications/{application_id}/hire", response_model=CandidateOut)
def hire_candidate(
    application_id: int,
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    application = _owned_application(application_id, current.id, db)
    application.status = ApplicationStatus.hired
    application.match_score = candidate_match_score_for_entities(
        application.student, application.job
    )
    NotificationService.notify(
        db,
        user_email=application.student.email,
        user_role="candidate",
        type=NotificationType.system,
        title="Félicitations — vous êtes retenu(e)",
        message=(
            f"Votre candidature pour {application.job.title} a été acceptée "
            f"par {current.company_name}."
        ),
        also_email=True,
        email_subject=f"Offre acceptée — {application.job.title}",
    )
    record_audit(
        db,
        actor_email=current.email,
        actor_role="recruiter",
        action=AuditAction.HIRE_APPLICATION,
        resource=str(application.id),
        details=f"{application.student.email} · {application.job.title}",
    )
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
        f"{current.company_name} would like to invite you for an interview "
        f"for {application.job.title} on {payload.interview_at.isoformat()}.\n\n"
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
    application.match_score = candidate_match_score_for_entities(
        application.student, application.job
    )
    NotificationService.notify(
        db,
        user_email=application.student.email,
        user_role="candidate",
        type=NotificationType.interview,
        title="Invitation à un entretien",
        message=message,
    )
    record_audit(
        db,
        actor_email=current.email,
        actor_role="recruiter",
        action=AuditAction.INVITE_INTERVIEW,
        resource=str(application.id),
        details=f"{application.student.email} · {payload.interview_at.isoformat()}",
    )
    db.commit()
    db.refresh(application)
    return _candidate_out(application, application.match_score)


@router.get(
    "/applications/{application_id}/cv/extracted", response_model=CvExtractedTextOut
)
def get_applicant_cv_text(
    application_id: int,
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    application = _owned_application(application_id, current.id, db)
    student = application.student
    if not student.cv_filename:
        raise HTTPException(status_code=404, detail="Applicant has no CV")
    return CvExtractedTextOut(**CvService.get_extracted(student))


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


def _candidate_out(
    application: Application,
    score: int,
    *,
    rank: int | None = None,
    rank_label: str | None = None,
    breakdown=None,
    explanation: str | None = None,
) -> CandidateOut:
    from app.schemas.matching import ScoreBreakdownOut

    student: Student = application.student
    breakdown_out = None
    if breakdown is not None:
        breakdown_out = ScoreBreakdownOut(
            skills_score=round(breakdown.skills_score * 100),
            experience_score=round(breakdown.experience_score * 100),
            semantic_score=round(breakdown.semantic_score * 100),
            education_score=round(breakdown.education_score * 100),
            location_score=round(breakdown.location_score * 100),
            availability_score=round(breakdown.availability_score * 100),
            matched_skills=breakdown.matched_skills,
            missing_skills=breakdown.missing_skills,
        )
    return CandidateOut(
        id=student.id,
        email=student.email,
        first_name=student.first_name,
        last_name=student.last_name,
        phone=student.phone,
        university=student.university,
        field_of_study=student.field_of_study,
        graduation_year=student.graduation_year,
        bio=student.bio,
        skills=student.skills,
        technical_skills=student.technical_skills,
        soft_skills=student.soft_skills,
        experiences=student.experiences,
        projects=student.projects,
        certifications=student.certifications,
        languages=student.languages,
        internship_type=student.internship_type,
        internship_duration=student.internship_duration,
        account_kind=getattr(student, "account_kind", None) or "candidate",
        cv_filename=student.cv_filename,
        created_at=student.created_at,
        application_id=application.id,
        application_status=application.status,
        match_score=score,
        rank=rank,
        rank_label=rank_label,
        breakdown=breakdown_out,
        explanation=explanation,
    )
