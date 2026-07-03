import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class Admin(Base):
    __tablename__ = "admins"
    id:              Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email:           Mapped[str]        = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str]        = mapped_column(String(255), nullable=False)
    first_name:      Mapped[str]        = mapped_column(String(100), nullable=False)
    last_name:       Mapped[str]        = mapped_column(String(100), nullable=False)
    is_superadmin:   Mapped[bool]       = mapped_column(Boolean, default=False)
    is_active:       Mapped[bool]       = mapped_column(Boolean, default=True)
    created_at:      Mapped[datetime]   = mapped_column(DateTime, server_default=func.now())
