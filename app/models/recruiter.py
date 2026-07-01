import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Recruiter(Base):
    __tablename__ = "recruiters"

    id:              Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email:           Mapped[str]        = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str]        = mapped_column(String(255), nullable=False)
    first_name:      Mapped[str]        = mapped_column(String(100), nullable=False)
    last_name:       Mapped[str]        = mapped_column(String(100), nullable=False)
    company:         Mapped[str | None] = mapped_column(String(255))
    job_title:       Mapped[str | None] = mapped_column(String(255))
    created_at:      Mapped[datetime]   = mapped_column(DateTime, server_default=func.now())

    jobs            = relationship("Job",                back_populates="recruiter",  cascade="all, delete-orphan")
    interviews      = relationship("RecruiterInterview", back_populates="recruiter",  cascade="all, delete-orphan")
    interview_slots = relationship("InterviewSlot",      back_populates="recruiter",  cascade="all, delete-orphan")
