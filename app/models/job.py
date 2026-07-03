import uuid
import enum
import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base

class JobType(str, enum.Enum):
    full_time  = "full_time"
    part_time  = "part_time"
    internship = "internship"
    remote     = "remote"

class JobStatus(str, enum.Enum):
    open   = "open"
    closed = "closed"
    draft  = "draft"

class Job(Base):
    __tablename__ = "jobs"
    id           = Column(Integer, primary_key=True, index=True)
    recruiter_id = Column(UUID(as_uuid=True), ForeignKey("recruiters.id", ondelete="CASCADE"), nullable=False)
    title        = Column(String(255), nullable=False)
    description  = Column(Text, nullable=False)
    requirements = Column(Text, nullable=True)
    location     = Column(String(255), nullable=True)
    type         = Column(Enum(JobType),   default=JobType.full_time)
    status       = Column(Enum(JobStatus), default=JobStatus.open)
    is_active    = Column(Boolean, default=True)
    created_at   = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at   = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    recruiter       = relationship("Recruiter",    back_populates="jobs")
    applications    = relationship("Application",  back_populates="job",  cascade="all, delete-orphan")
    interview_slots = relationship("InterviewSlot", back_populates="job", cascade="all, delete-orphan")
