from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.interview import InterviewSlot, InterviewStatus
from datetime import datetime

router = APIRouter(prefix="/interviews", tags=["interviews"])

@router.post("/slots")
def create_slot(recruiter_id: int, scheduled_at: datetime, db: Session = Depends(get_db)):
    slot = InterviewSlot(recruiter_id=recruiter_id, scheduled_at=scheduled_at)
    db.add(slot); db.commit(); db.refresh(slot)
    return slot

@router.post("/book/{slot_id}")
def book_slot(slot_id: int, student_id: int, db: Session = Depends(get_db)):
    slot = db.query(InterviewSlot).filter(InterviewSlot.id == slot_id).first()
    slot.student_id = student_id
    slot.status = InterviewStatus.booked
    db.commit()
    return slot

@router.get("/me")
def my_interviews(student_id: int, db: Session = Depends(get_db)):
    return db.query(InterviewSlot).filter(InterviewSlot.student_id == student_id).all()