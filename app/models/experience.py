"""
Experience Model for Recruitment Platform
Optimized for candidate work history, skills, and tenure tracking
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Text, DateTime, func, Enum, Integer, ForeignKey, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class ExperienceLevel(str, enum.Enum):
    """Employment level classification"""
    entry = "entry"
    junior = "junior"
    mid = "mid"
    senior = "senior"
    lead = "lead"
    manager = "manager"
    director = "director"
    executive = "executive"


class EmploymentType(str, enum.Enum):
    """Employment contract type"""
    full_time = "full_time"
    part_time = "part_time"
    contract = "contract"
    freelance = "freelance"
    internship = "internship"
    temporary = "temporary"


class ExperienceStatus(str, enum.Enum):
    """Experience verification status"""
    pending = "pending"
    verified = "verified"
    unverified = "unverified"
    disputed = "disputed"


class Experience(Base):
    """Candidate work experience records"""
    __tablename__ = "experiences"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        index=True
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Job details
    job_title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    location: Mapped[str | None] = mapped_column(String(255))
    
    # Employment info
    employment_type: Mapped[str] = mapped_column(
        Enum(EmploymentType), 
        default=EmploymentType.full_time
    )
    level: Mapped[str] = mapped_column(
        Enum(ExperienceLevel), 
        default=ExperienceLevel.mid,
        index=True
    )
    
    # Duration tracking
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    end_date: Mapped[datetime | None] = mapped_column(DateTime)
    years_of_experience: Mapped[float] = mapped_column(Float, default=0.0)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    # Responsibilities and achievements
    description: Mapped[str | None] = mapped_column(Text)
    responsibilities: Mapped[str | None] = mapped_column(Text)
    achievements: Mapped[str | None] = mapped_column(Text)
    
    # Skills and technologies
    technologies_used: Mapped[str | None] = mapped_column(Text)
    key_skills: Mapped[str | None] = mapped_column(Text)
    
    # Salary (optional)
    salary_min: Mapped[float | None] = mapped_column(Float)
    salary_max: Mapped[float | None] = mapped_column(Float)
    salary_currency: Mapped[str | None] = mapped_column(String(3))
    
    # Verification and status
    status: Mapped[str] = mapped_column(
        Enum(ExperienceStatus), 
        default=ExperienceStatus.unverified,
        index=True
    )
    verified_by: Mapped[str | None] = mapped_column(String(255))
    verification_date: Mapped[datetime | None] = mapped_column(DateTime)
    verification_notes: Mapped[str | None] = mapped_column(Text)
    
    # Additional fields
    industry: Mapped[str | None] = mapped_column(String(100), index=True)
    company_size: Mapped[str | None] = mapped_column(String(50))
    department: Mapped[str | None] = mapped_column(String(100))
    reports_to: Mapped[str | None] = mapped_column(String(255))
    team_size: Mapped[int | None] = mapped_column(Integer)
    
    # Metadata
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    candidate = relationship("Candidate", foreign_keys=[candidate_id])


class SkillsMatrix(Base):
    """Structured skills gained from experience"""
    __tablename__ = "skills_matrix"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    experience_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("experiences.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    proficiency_level: Mapped[str] = mapped_column(
        Enum(ExperienceLevel),
        default=ExperienceLevel.mid
    )
    years_used: Mapped[float] = mapped_column(Float, default=1.0)
    last_used: Mapped[datetime | None] = mapped_column(DateTime)
    is_endorsed: Mapped[bool] = mapped_column(Boolean, default=False)
    endorsement_count: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    experience = relationship("Experience", foreign_keys=[experience_id])
