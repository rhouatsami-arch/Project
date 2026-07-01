import enum
from datetime import datetime
from sqlalchemy import String, Text, DateTime, func, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid

class RecruiterInterview(Base):
    __tablename__ = "recruiter_interviews"
    id:           Mapped[int]           = mapped_column(primary_key=True, index=True)
    recruiter_id: Mapped[uuid.UUID]     = mapped_column(UUID(as_uuid=True), ForeignKey("recruiters.id", ondelete="CASCADE"))
    student_id:   Mapped[uuid.UUID]     = mapped_column(UUID(as_uuid=True), ForeignKey("students.id",   ondelete="CASCADE"))
    job_title:    Mapped[str | None]    = mapped_column(String(255))
    scheduled_at: Mapped[datetime]      = mapped_column(DateTime, nullable=False)
    duration_min: Mapped[int]           = mapped_column(Integer, default=30)
    meeting_link: Mapped[str | None]    = mapped_column(String(500))
    notes:        Mapped[str | None]    = mapped_column(Text)
    status:       Mapped[str]           = mapped_column(String(20), default="scheduled")
    ats_score:    Mapped[int | None]    = mapped_column(Integer)
    created_at:   Mapped[datetime]      = mapped_column(DateTime, server_default=func.now())
    recruiter = relationship("Recruiter", back_populates="interviews")
    student   = relationship("Student")
