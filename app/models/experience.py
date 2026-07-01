import enum
import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class ExperienceType(str, enum.Enum):
    internship  = "internship"
    full_time   = "full_time"
    part_time   = "part_time"
    freelance   = "freelance"
    volunteer   = "volunteer"
    project     = "project"


class Experience(Base):
    __tablename__ = "experiences"

    id           = Column(Integer, primary_key=True, index=True)
    student_id   = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    title        = Column(String(255), nullable=False)
    company      = Column(String(255), nullable=False)
    location     = Column(String(255), nullable=True)
    type         = Column(Enum(ExperienceType), default=ExperienceType.full_time)
    description  = Column(Text, nullable=True)
    skills_used  = Column(Text, nullable=True)       # comma-separated skills
    start_date   = Column(DateTime, nullable=False)
    end_date     = Column(DateTime, nullable=True)   # null = current job
    is_current   = Column(Boolean, default=False)
    created_at   = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at   = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    student = relationship("Student", back_populates="experiences")
