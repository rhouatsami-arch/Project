import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Text, DateTime, func, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class StudentRole(str, enum.Enum):
    student    = "student"
    internship = "internship"
    stage      = "stage"


class Student(Base):
    __tablename__ = "students"

    id:              Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email:           Mapped[str]        = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str]        = mapped_column(String(255), nullable=False)
    first_name:      Mapped[str]        = mapped_column(String(100), nullable=False)
    last_name:       Mapped[str]        = mapped_column(String(100), nullable=False)
    school:          Mapped[str | None] = mapped_column(String(255))
    field_of_study:  Mapped[str | None] = mapped_column(String(255))
    graduation_year: Mapped[int | None] = mapped_column()
    bio:             Mapped[str | None] = mapped_column(Text)
    skills:          Mapped[str | None] = mapped_column(Text)
    linkedin_url:    Mapped[str | None] = mapped_column(String(500))
    github_url:      Mapped[str | None] = mapped_column(String(500))
    cv_url:          Mapped[str | None] = mapped_column(String(500))
    is_visible:      Mapped[bool]       = mapped_column(default=True)
    role:            Mapped[str | None] = mapped_column(Enum(StudentRole), default=StudentRole.student)
    internship_duration_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at:      Mapped[datetime]   = mapped_column(DateTime, server_default=func.now())
    updated_at:      Mapped[datetime]   = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    applications    = relationship("Application",  back_populates="student", cascade="all, delete-orphan")
    interview_slots = relationship("InterviewSlot", back_populates="student")
