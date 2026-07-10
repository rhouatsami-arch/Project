from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from app.database import get_db
from app.models.recruiter_interview import RecruiterInterview
from app.auth import get_current_recruiter, get_current_student
from app.models.student import Student

router = APIRouter(prefix="/meetings", tags=["meeting-scheduling"])

class MeetingCreate(BaseModel):
    student_id:   str
    job_title:    str | None = None
    scheduled_at: datetime
    duration_min: int        = 30
    meeting_link: str | None = None
    notes:        str | None = None

class MeetingUpdate(BaseModel):
    scheduled_at: datetime    | None = None
    duration_min: int         | None = None
    meeting_link: str         | None = None
    notes:        str         | None = None
    status:       str         | None = None

@router.post("/schedule", status_code=201)
def schedule_meeting(
    payload: MeetingCreate,
    current  = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    meeting = RecruiterInterview(
        recruiter_id=current.id,
        student_id=payload.student_id,
        job_title=payload.job_title,
        scheduled_at=payload.scheduled_at,
        duration_min=payload.duration_min,
        meeting_link=payload.meeting_link,
        notes=payload.notes,
    )
    db.add(meeting); db.commit(); db.refresh(meeting)
    return {"id": meeting.id, "student_id": str(meeting.student_id),
            "scheduled_at": str(meeting.scheduled_at), "status": meeting.status,
            "meeting_link": meeting.meeting_link}

@router.get("/my")
def my_meetings_recruiter(
    status: str | None = Query(None),
    current = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    q = db.query(RecruiterInterview).filter(RecruiterInterview.recruiter_id == current.id)
    if status: q = q.filter(RecruiterInterview.status == status)
    return [{"id":m.id,"student_id":str(m.student_id),"job_title":m.job_title,
             "scheduled_at":str(m.scheduled_at),"status":m.status,"meeting_link":m.meeting_link}
            for m in q.order_by(RecruiterInterview.scheduled_at).all()]

@router.get("/student/my")
def my_meetings_student(
    current: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    meetings = db.query(RecruiterInterview).filter(
        RecruiterInterview.student_id == current.id).all()
    return [{"id":m.id,"recruiter_id":str(m.recruiter_id),"job_title":m.job_title,
             "scheduled_at":str(m.scheduled_at),"status":m.status,"meeting_link":m.meeting_link}
            for m in meetings]

@router.patch("/{mid}")
def update_meeting(
    mid: int,
    payload: MeetingUpdate,
    current = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    m = db.query(RecruiterInterview).filter(
        RecruiterInterview.id == mid,
        RecruiterInterview.recruiter_id == current.id).first()
    if not m: raise HTTPException(404, "Not found")
    for k,v in payload.model_dump(exclude_unset=True).items(): setattr(m,k,v)
    db.commit(); db.refresh(m)
    return {"id":m.id,"status":m.status,"scheduled_at":str(m.scheduled_at)}

@router.delete("/{mid}", status_code=204)
def cancel_meeting(mid: int, current = Depends(get_current_recruiter), db: Session = Depends(get_db)):
    m = db.query(RecruiterInterview).filter(
        RecruiterInterview.id == mid,
        RecruiterInterview.recruiter_id == current.id).first()
    if not m: raise HTTPException(404, "Not found")
    db.delete(m); db.commit()

@router.get("/availability/{student_id}")
def check_availability(
    student_id: str,
    current = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    booked = db.query(RecruiterInterview).filter(
        RecruiterInterview.student_id == student_id,
        RecruiterInterview.status.in_(["scheduled","confirmed"])).all()
    return {"student_id": student_id,
            "booked_slots": [{"scheduled_at":str(m.scheduled_at),"duration_min":m.duration_min} for m in booked]}
