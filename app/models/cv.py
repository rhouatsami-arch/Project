import enum
import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class CVStatus(str, enum.Enum):
    uploaded   = "uploaded"
    processing = "processing"
    extracted  = "extracted"
    failed     = "failed"


class CV(Base):
    __tablename__ = "cvs"

    id            = Column(Integer, primary_key=True, index=True)
    student_id    = Column(UUID(as_uuid=True), ForeignKey("students.id", ondelete="CASCADE"), nullable=True)
    candidate_id  = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=True)
    filename      = Column(String(255), nullable=False)
    file_path     = Column(String(500), nullable=False)
    file_size     = Column(Integer, nullable=False)
    file_ext      = Column(String(10), nullable=False)
    status        = Column(Enum(CVStatus), default=CVStatus.uploaded)
    raw_text      = Column(Text, nullable=True)
    extracted_data= Column(Text, nullable=True)   # JSON string: emails, phones, skills, etc
    is_current    = Column(Boolean, default=True) # latest CV for this user
    uploaded_at   = Column(DateTime, default=datetime.datetime.utcnow)
    processed_at  = Column(DateTime, nullable=True)
