from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session, joinedload

from app.auth import (
    create_calendar_oauth_state_token,
    decode_calendar_oauth_state_token,
    get_current_candidate,
    get_current_recruiter,
    get_current_student,
)
from app.database import get_db
from app.models.platform import GoogleCalendarConnection
from app.models.recruitment import Application, Job, Recruiter, Student
from app.modules.platform.audit import AuditAction, record_audit
from app.modules.platform.google_calendar_service import (
    GoogleCalendarService,
    calendar_frontend_redirect,
    is_calendar_configured,
    token_expires_at,
)
from app.modules.platform.meeting_calendar_sync import MeetingCalendarSync
from app.modules.platform.service import MeetingService
from app.schemas.platform import (
    AvailabilityCreate,
    AvailabilityOut,
    GoogleCalendarStatusOut,
    InterviewSlotCreate,
    InterviewSlotOut,
    MeetingCreate,
    MeetingOut,
    MeetingPropose,
    MeetingReschedule,
)
from app.utils.datetime import utc_now

router = APIRouter(prefix="/meetings", tags=["meetings", "interviews"])


def _parse_dt(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is not None:
        return dt.astimezone(UTC).replace(tzinfo=None)
    return dt


def _meeting_out(meeting) -> MeetingOut:
    return MeetingOut(
        id=meeting.id,
        application_id=meeting.application_id,
        job_id=meeting.job_id,
        scheduled_at=meeting.scheduled_at.isoformat(),
        location=meeting.location,
        notes=meeting.notes,
        status=(
            meeting.status if isinstance(meeting.status, str) else meeting.status.value
        ),
        slot_id=meeting.slot_id,
        updated_at=meeting.updated_at.isoformat() if meeting.updated_at else None,
        google_event_link=meeting.google_event_link,
        google_meet_link=meeting.google_meet_link,
    )


def _slot_out(slot) -> InterviewSlotOut:
    return InterviewSlotOut(
        id=slot.id,
        starts_at=slot.starts_at.isoformat(),
        ends_at=slot.ends_at.isoformat(),
        is_booked=slot.is_booked,
    )


def _availability_out(window) -> AvailabilityOut:
    return AvailabilityOut(
        id=window.id,
        starts_at=window.starts_at.isoformat(),
        ends_at=window.ends_at.isoformat(),
    )


def _owned_application(
    application_id: int, recruiter: Recruiter, db: Session
) -> Application:
    application = (
        db.query(Application)
        .options(joinedload(Application.job), joinedload(Application.student))
        .join(Job)
        .filter(
            Application.id == application_id,
            Job.recruiter_id == recruiter.id,
        )
        .first()
    )
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


def _audit_student(
    db: Session,
    student: Student,
    action: str,
    resource: str,
    details: str | None = None,
) -> None:
    role = getattr(student, "account_kind", None) or "student"
    record_audit(
        db,
        actor_email=student.email,
        actor_role=role,
        action=action,
        resource=resource,
        details=details,
    )


def _audit_recruiter(
    db: Session,
    recruiter: Recruiter,
    action: str,
    resource: str,
    details: str | None = None,
) -> None:
    record_audit(
        db,
        actor_email=recruiter.email,
        actor_role="recruiter",
        action=action,
        resource=resource,
        details=details,
    )


@router.post("/slots", response_model=InterviewSlotOut, status_code=201)
def create_slot(
    payload: InterviewSlotCreate,
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    try:
        slot = MeetingService.create_slot(
            db,
            recruiter=current,
            starts_at=_parse_dt(payload.starts_at),
            ends_at=_parse_dt(payload.ends_at),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(slot)
    _audit_recruiter(
        db,
        current,
        AuditAction.CREATE_INTERVIEW_SLOT,
        str(slot.id),
        f"{slot.starts_at.isoformat()} → {slot.ends_at.isoformat()}",
    )
    db.commit()
    return _slot_out(slot)


@router.get("/slots/me", response_model=list[InterviewSlotOut])
def list_my_slots(
    current: Recruiter = Depends(get_current_recruiter), db: Session = Depends(get_db)
):
    return [_slot_out(s) for s in MeetingService.list_slots(db, current)]


@router.delete("/slots/{slot_id}", status_code=204)
def delete_slot(
    slot_id: int,
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    try:
        MeetingService.delete_slot(db, recruiter=current, slot_id=slot_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    _audit_recruiter(db, current, AuditAction.DELETE_INTERVIEW_SLOT, str(slot_id))
    db.commit()


@router.post("/availability", response_model=AvailabilityOut, status_code=201)
def add_availability_candidate(
    payload: AvailabilityCreate,
    current: Student = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    return _add_availability(payload, current, db)


@router.post("/students/availability", response_model=AvailabilityOut, status_code=201)
def add_availability_student(
    payload: AvailabilityCreate,
    current: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    return _add_availability(payload, current, db)


def _add_availability(payload: AvailabilityCreate, student: Student, db: Session):
    try:
        window = MeetingService.add_availability(
            db,
            student=student,
            starts_at=_parse_dt(payload.starts_at),
            ends_at=_parse_dt(payload.ends_at),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(window)
    _audit_student(db, student, AuditAction.ADD_AVAILABILITY, str(window.id))
    db.commit()
    return _availability_out(window)


@router.get("/availability/me", response_model=list[AvailabilityOut])
def list_availability_candidate(
    current: Student = Depends(get_current_candidate), db: Session = Depends(get_db)
):
    return [_availability_out(w) for w in MeetingService.list_availability(db, current)]


@router.get("/students/availability/me", response_model=list[AvailabilityOut])
def list_availability_student(
    current: Student = Depends(get_current_student), db: Session = Depends(get_db)
):
    return [_availability_out(w) for w in MeetingService.list_availability(db, current)]


@router.delete("/availability/{availability_id}", status_code=204)
def delete_availability_candidate(
    availability_id: int,
    current: Student = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    return _delete_availability(availability_id, current, db)


@router.delete("/students/availability/{availability_id}", status_code=204)
def delete_availability_student(
    availability_id: int,
    current: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    return _delete_availability(availability_id, current, db)


def _delete_availability(availability_id: int, student: Student, db: Session):
    try:
        MeetingService.delete_availability(
            db, student=student, availability_id=availability_id
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    _audit_student(db, student, AuditAction.DELETE_AVAILABILITY, str(availability_id))
    db.commit()


@router.post("/propose-best", response_model=MeetingOut, status_code=201)
def propose_best_slot(
    payload: MeetingPropose,
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    application = _owned_application(payload.application_id, current, db)
    try:
        meeting = MeetingService.propose_best(
            db,
            application=application,
            recruiter=current,
            location=payload.location,
            notes=payload.notes,
            slot_id=payload.slot_id,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    db.commit()
    db.refresh(meeting)
    _audit_recruiter(
        db,
        current,
        AuditAction.PROPOSE_MEETING,
        str(meeting.id),
        f"application:{application.id}",
    )
    db.commit()
    return _meeting_out(meeting)


@router.post("/", response_model=MeetingOut, status_code=201)
def schedule_meeting(
    payload: MeetingCreate,
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    application = _owned_application(payload.application_id, current, db)
    meeting = MeetingService.schedule(
        db,
        application=application,
        recruiter=current,
        scheduled_at=_parse_dt(payload.scheduled_at),
        location=payload.location,
        notes=payload.notes,
    )
    db.commit()
    db.refresh(meeting)
    _audit_recruiter(
        db,
        current,
        AuditAction.SCHEDULE_MEETING,
        str(meeting.id),
        f"application:{application.id}",
    )
    db.commit()
    return _meeting_out(meeting)


@router.post("/{meeting_id}/confirm", response_model=MeetingOut)
def confirm_meeting_candidate(
    meeting_id: int,
    current: Student = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    return _confirm(meeting_id, current, db)


@router.post("/students/{meeting_id}/confirm", response_model=MeetingOut)
def confirm_meeting_student(
    meeting_id: int,
    current: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    return _confirm(meeting_id, current, db)


def _confirm(meeting_id: int, student: Student, db: Session):
    try:
        meeting = MeetingService.confirm(db, meeting_id=meeting_id, student=student)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    MeetingCalendarSync.sync_on_accepted(db, meeting)
    db.commit()
    db.refresh(meeting)
    _audit_student(db, student, AuditAction.CONFIRM_MEETING, str(meeting.id))
    db.commit()
    return _meeting_out(meeting)


@router.post("/{meeting_id}/refuse", response_model=MeetingOut)
def refuse_meeting_candidate(
    meeting_id: int,
    current: Student = Depends(get_current_candidate),
    db: Session = Depends(get_db),
):
    return _refuse(meeting_id, current, db)


@router.post("/students/{meeting_id}/refuse", response_model=MeetingOut)
def refuse_meeting_student(
    meeting_id: int,
    current: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    return _refuse(meeting_id, current, db)


def _refuse(meeting_id: int, student: Student, db: Session):
    try:
        meeting = MeetingService.refuse(db, meeting_id=meeting_id, student=student)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(meeting)
    _audit_student(db, student, AuditAction.REFUSE_MEETING, str(meeting.id))
    db.commit()
    return _meeting_out(meeting)


@router.post("/{meeting_id}/cancel", response_model=MeetingOut)
def cancel_meeting_recruiter(
    meeting_id: int,
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    try:
        meeting = MeetingService.cancel(
            db, meeting_id=meeting_id, actor_recruiter=current
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    MeetingCalendarSync.sync_on_cancelled(db, meeting)
    db.commit()
    db.refresh(meeting)
    _audit_recruiter(db, current, AuditAction.CANCEL_MEETING, str(meeting.id))
    db.commit()
    return _meeting_out(meeting)


@router.post("/{meeting_id}/reschedule", response_model=MeetingOut)
def reschedule_meeting(
    meeting_id: int,
    payload: MeetingReschedule,
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    try:
        meeting = MeetingService.reschedule(
            db,
            meeting_id=meeting_id,
            recruiter=current,
            scheduled_at=_parse_dt(payload.scheduled_at)
            if payload.scheduled_at
            else None,
            slot_id=payload.slot_id,
            location=payload.location,
            notes=payload.notes,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    MeetingCalendarSync.sync_on_rescheduled(db, meeting)
    db.commit()
    db.refresh(meeting)
    _audit_recruiter(db, current, AuditAction.RESCHEDULE_MEETING, str(meeting.id))
    db.commit()
    return _meeting_out(meeting)


@router.post("/{meeting_id}/complete", response_model=MeetingOut)
def complete_meeting(
    meeting_id: int,
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    try:
        meeting = MeetingService.complete(db, meeting_id=meeting_id, recruiter=current)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()
    db.refresh(meeting)
    _audit_recruiter(db, current, AuditAction.COMPLETE_MEETING, str(meeting.id))
    db.commit()
    return _meeting_out(meeting)


@router.get("/recruiter/me", response_model=list[MeetingOut])
def recruiter_meetings(
    current: Recruiter = Depends(get_current_recruiter), db: Session = Depends(get_db)
):
    return [_meeting_out(m) for m in MeetingService.list_for_recruiter(db, current)]


@router.get("/google/status", response_model=GoogleCalendarStatusOut)
def google_calendar_status(
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    connection = (
        db.query(GoogleCalendarConnection)
        .filter(GoogleCalendarConnection.recruiter_id == current.id)
        .first()
    )
    return GoogleCalendarStatusOut(
        configured=is_calendar_configured(),
        connected=connection is not None,
        google_email=connection.google_email if connection else None,
    )


@router.get("/google/authorize")
def google_calendar_authorize(
    current: Recruiter = Depends(get_current_recruiter),
):
    if not is_calendar_configured():
        raise HTTPException(
            status_code=503,
            detail="Google Calendar is not configured on this server",
        )
    state = create_calendar_oauth_state_token(current.email)
    return {"authorization_url": GoogleCalendarService.build_authorize_url(state)}


@router.get("/google/callback")
def google_calendar_callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: Session = Depends(get_db),
):
    frontend = calendar_frontend_redirect()
    if error:
        return RedirectResponse(f"{frontend}?google_calendar=error")
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing OAuth code or state")
    recruiter_email = decode_calendar_oauth_state_token(state)
    recruiter = db.query(Recruiter).filter(Recruiter.email == recruiter_email).first()
    if not recruiter:
        raise HTTPException(status_code=404, detail="Recruiter not found")
    try:
        token_data = GoogleCalendarService.exchange_code(code)
    except Exception as exc:
        raise HTTPException(
            status_code=400, detail=f"Google token exchange failed: {exc}"
        ) from exc
    refresh_token = token_data.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=400,
            detail="Google did not return a refresh token; revoke app access and retry",
        )
    access_token = token_data.get("access_token", "")
    google_email = GoogleCalendarService.fetch_user_email(access_token)
    connection = (
        db.query(GoogleCalendarConnection)
        .filter(GoogleCalendarConnection.recruiter_id == recruiter.id)
        .first()
    )
    if connection:
        connection.refresh_token = refresh_token
        connection.access_token = access_token
        connection.token_expires_at = token_expires_at(token_data.get("expires_in"))
        connection.google_email = google_email or connection.google_email
        connection.updated_at = utc_now()
    else:
        db.add(
            GoogleCalendarConnection(
                recruiter_id=recruiter.id,
                refresh_token=refresh_token,
                access_token=access_token,
                token_expires_at=token_expires_at(token_data.get("expires_in")),
                google_email=google_email,
            )
        )
    db.commit()
    return RedirectResponse(f"{frontend}?google_calendar=connected")


@router.delete("/google/disconnect", status_code=204)
def google_calendar_disconnect(
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    connection = (
        db.query(GoogleCalendarConnection)
        .filter(GoogleCalendarConnection.recruiter_id == current.id)
        .first()
    )
    if connection:
        db.delete(connection)
        db.commit()


@router.get("/students/me", response_model=list[MeetingOut])
def student_meetings(
    current: Student = Depends(get_current_student), db: Session = Depends(get_db)
):
    return [_meeting_out(m) for m in MeetingService.list_for_student(db, current)]


@router.get("/candidates/me", response_model=list[MeetingOut])
def candidate_meetings(
    current: Student = Depends(get_current_candidate), db: Session = Depends(get_db)
):
    return [_meeting_out(m) for m in MeetingService.list_for_student(db, current)]
