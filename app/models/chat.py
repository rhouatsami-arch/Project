import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id          = Column(Integer, primary_key=True, index=True)
    session_key = Column(String(100), unique=True, index=True, nullable=False)
    student_id  = Column(Integer, nullable=True)
    created_at  = Column(DateTime, default=datetime.datetime.utcnow)
    messages    = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id         = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role       = Column(String(20), nullable=False)
    content    = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    session    = relationship("ChatSession", back_populates="messages")
