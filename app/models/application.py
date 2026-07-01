import uuid
import enum
import datetime
from sqlalchemy import Column, Integer, Text, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class ApplicationStatus(str, enum.Enum):
    pending     = "pending"
    reviewed    = "reviewed"
    shortlisted = "shortlisted"
    accepted    = "accepted"
    rejected    = "rejected"

class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("student_id", "job_id", name="uq_student_job"),)
    id             = Column(Integer, primary_key=True, index=True)
    student_id     = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    job_id         = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    status         = Column(Enum(ApplicationStatus), default=ApplicationStatus.pending)
    cover_letter   = Column(Text, nullable=True)
    ats_score      = Column(Integer, nullable=True)
    ai_match_score = Column(Integer, nullable=True)
    applied_at     = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at     = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    student         = relationship("Student",       back_populates="applications")
    job             = relationship("Job",           back_populates="applications")
    interview_slots = relationship("InterviewSlot", back_populates="application")
