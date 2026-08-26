import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.datetime import utc_now


class ApplicationStatus(enum.StrEnum):
    applied = "applied"
    shortlisted = "shortlisted"
    interview_invited = "interview_invited"
    rejected = "rejected"
    hired = "hired"


class JobStatus(enum.StrEnum):
    open = "open"
    closed = "closed"


class InternshipDurationType(enum.StrEnum):
    observation = "observation"
    operational = "operational"
    functional = "functional"


INTERNSHIP_DURATION_LABELS: dict[InternshipDurationType, str] = {
    InternshipDurationType.observation: (
        "Observation internship: Short-term (1 to 2 weeks)"
    ),
    InternshipDurationType.operational: (
        "Operational internship: Lasting 1 to 3 months"
    ),
    InternshipDurationType.functional: (
        "Functional internship: Duration of 4 to 6 months"
    ),
}


def parse_internship_duration_type(
    value: str | InternshipDurationType | None,
) -> InternshipDurationType | None:
    if value is None:
        return None
    if isinstance(value, InternshipDurationType):
        return value

    normalized = value.strip().lower()
    aliases = {
        "observation": InternshipDurationType.observation,
        "operational": InternshipDurationType.operational,
        "functional": InternshipDurationType.functional,
        "observation internship": InternshipDurationType.observation,
        "operational internship": InternshipDurationType.operational,
        "functional internship": InternshipDurationType.functional,
    }
    if normalized in aliases:
        return aliases[normalized]

    for duration_type, label in INTERNSHIP_DURATION_LABELS.items():
        if normalized == label.lower():
            return duration_type

    raise ValueError(
        "internship_duration must be one of: observation, operational, functional"
    )


class Student(Base):
    __tablename__ = "students"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30))
    university: Mapped[str | None] = mapped_column(String(255))
    field_of_study: Mapped[str | None] = mapped_column(String(255))
    graduation_year: Mapped[int | None] = mapped_column(Integer)
    bio: Mapped[str | None] = mapped_column(Text)
    skills: Mapped[str | None] = mapped_column(Text)
    technical_skills: Mapped[str | None] = mapped_column(Text)
    soft_skills: Mapped[str | None] = mapped_column(Text)
    experiences: Mapped[str | None] = mapped_column(Text)
    projects: Mapped[str | None] = mapped_column(Text)
    certifications: Mapped[str | None] = mapped_column(Text)
    languages: Mapped[str | None] = mapped_column(Text)
    internship_type: Mapped[str | None] = mapped_column(String(255))
    internship_duration: Mapped[str | None] = mapped_column(String(255))
    account_kind: Mapped[str] = mapped_column(String(30), default="student")
    cv_filename: Mapped[str | None] = mapped_column(String(255))
    cv_path: Mapped[str | None] = mapped_column(String(500))
    cv_extracted_text: Mapped[str | None] = mapped_column(Text)
    cv_extracted_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now
    )

    applications = relationship(
        "Application", back_populates="student", cascade="all, delete-orphan"
    )
    saved_jobs = relationship(
        "SavedJob", back_populates="student", cascade="all, delete-orphan"
    )


class Recruiter(Base):
    __tablename__ = "recruiters"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now
    )

    jobs = relationship("Job", back_populates="recruiter", cascade="all, delete-orphan")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    recruiter_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("recruiters.id", ondelete="CASCADE")
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    required_skills: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(255))
    employment_type: Mapped[str | None] = mapped_column(String(50), default="full_time")
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.open)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now
    )

    recruiter = relationship("Recruiter", back_populates="jobs")
    applications = relationship(
        "Application", back_populates="job", cascade="all, delete-orphan"
    )
    saved_by = relationship(
        "SavedJob", back_populates="job", cascade="all, delete-orphan"
    )


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint("student_id", "job_id", name="uq_student_job_application"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE")
    )
    job_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("jobs.id", ondelete="CASCADE")
    )
    cover_letter: Mapped[str | None] = mapped_column(Text)
    internship_type: Mapped[InternshipDurationType | None] = mapped_column(
        Enum(
            InternshipDurationType,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=True,
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus), default=ApplicationStatus.applied
    )
    match_score: Mapped[int] = mapped_column(Integer, default=0)
    interview_message: Mapped[str | None] = mapped_column(Text)
    interview_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now
    )

    student = relationship("Student", back_populates="applications")
    job = relationship("Job", back_populates="applications")


class SavedJob(Base):
    __tablename__ = "saved_jobs"
    __table_args__ = (
        UniqueConstraint("student_id", "job_id", name="uq_student_saved_job"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE")
    )
    job_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("jobs.id", ondelete="CASCADE")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)

    student = relationship("Student", back_populates="saved_jobs")
    job = relationship("Job", back_populates="saved_by")
