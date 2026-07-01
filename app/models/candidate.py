import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Text, DateTime, func, Enum, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class CandidateStatus(str, enum.Enum):
    active   = "active"
    inactive = "inactive"


class AppStatus(str, enum.Enum):
    pending   = "pending"
    reviewed  = "reviewed"
    accepted  = "accepted"
    rejected  = "rejected"
    cancelled = "cancelled"


class Candidate(Base):
    __tablename__ = "candidates"
    id:              Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email:           Mapped[str]        = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str]        = mapped_column(String(255), nullable=False)
    first_name:      Mapped[str]        = mapped_column(String(100), nullable=False)
    last_name:       Mapped[str]        = mapped_column(String(100), nullable=False)
    phone:           Mapped[str | None] = mapped_column(String(20))
    bio:             Mapped[str | None] = mapped_column(Text)
    skills:          Mapped[str | None] = mapped_column(Text)
    location:        Mapped[str | None] = mapped_column(String(255))
    linkedin_url:    Mapped[str | None] = mapped_column(String(500))
    github_url:      Mapped[str | None] = mapped_column(String(500))
    cv_url:          Mapped[str | None] = mapped_column(String(500))
    is_visible:      Mapped[bool]       = mapped_column(Boolean, default=True)
    status:          Mapped[str | None] = mapped_column(Enum(CandidateStatus), default=CandidateStatus.active)
    created_at:      Mapped[datetime]   = mapped_column(DateTime, server_default=func.now())
    updated_at:      Mapped[datetime]   = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    documents    = relationship("CandidateDocument",    back_populates="candidate", cascade="all, delete-orphan")
    applications = relationship("CandidateApplication", back_populates="candidate", cascade="all, delete-orphan")
    favorites    = relationship("CandidateFavorite",    back_populates="candidate", cascade="all, delete-orphan")


class CandidateDocument(Base):
    __tablename__ = "candidate_documents"
    id:           Mapped[int]       = mapped_column(primary_key=True, index=True)
    candidate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"))
    name:         Mapped[str]       = mapped_column(String(255))
    type:         Mapped[str]       = mapped_column(String(50))
    file_url:     Mapped[str]       = mapped_column(String(500))
    created_at:   Mapped[datetime]  = mapped_column(DateTime, server_default=func.now())
    candidate = relationship("Candidate", back_populates="documents")


class CandidateApplication(Base):
    __tablename__ = "candidate_applications"
    id:           Mapped[int]        = mapped_column(primary_key=True, index=True)
    candidate_id: Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"))
    job_id:       Mapped[int]        = mapped_column(Integer, nullable=False)
    status:       Mapped[str]        = mapped_column(Enum(AppStatus), default=AppStatus.pending)
    cover_letter: Mapped[str | None] = mapped_column(Text)
    applied_at:   Mapped[datetime]   = mapped_column(DateTime, server_default=func.now())
    updated_at:   Mapped[datetime]   = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    candidate = relationship("Candidate", back_populates="applications")


class CandidateFavorite(Base):
    __tablename__ = "candidate_favorites"
    id:           Mapped[int]       = mapped_column(primary_key=True, index=True)
    candidate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"))
    job_id:       Mapped[int]       = mapped_column(Integer, nullable=False)
    saved_at:     Mapped[datetime]  = mapped_column(DateTime, server_default=func.now())
    candidate = relationship("Candidate", back_populates="favorites")
