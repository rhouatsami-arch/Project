import uuid
import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import enum

class SlotStatus(str, enum.Enum):
    available = "available"
    booked    = "booked"
    completed = "completed"
    cancelled = "cancelled"

class InterviewSlot(Base):
    __tablename__ = "interview_slots"
    id             = Column(Integer, primary_key=True, index=True)
    recruiter_id   = Column(UUID(as_uuid=True), ForeignKey("recruiters.id", ondelete="CASCADE"), nullable=False)
    job_id         = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="SET NULL"), nullable=True)
    student_id     = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="SET NULL"), nullable=True)
    scheduled_at   = Column(DateTime, nullable=False)
    duration_min   = Column(Integer, default=30)
    meeting_link   = Column(String(500), nullable=True)
    status         = Column(Enum(SlotStatus), default=SlotStatus.available)
    created_at     = Column(DateTime, default=datetime.datetime.utcnow)
    recruiter   = relationship("Recruiter", back_populates="interview_slots")
    job         = relationship("Job",       back_populates="interview_slots")
    application = relationship("Application", back_populates="interview_slots")
    student     = relationship("Student",   back_populates="interview_slots")
