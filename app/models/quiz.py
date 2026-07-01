import enum
from datetime import datetime
from sqlalchemy import String, Text, DateTime, func, ForeignKey, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class DifficultyLevel(str, enum.Enum):
    easy   = "easy"
    medium = "medium"
    hard   = "hard"

class Quiz(Base):
    __tablename__ = "quizzes"
    id:          Mapped[int]        = mapped_column(primary_key=True, index=True)
    title:       Mapped[str]        = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    topic:       Mapped[str | None] = mapped_column(String(100))
    difficulty:  Mapped[str | None] = mapped_column(String(20), default=DifficultyLevel.medium)
    created_at:  Mapped[datetime]   = mapped_column(DateTime, server_default=func.now())
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    attempts  = relationship("QuizAttempt",  back_populates="quiz", cascade="all, delete-orphan")

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    id:             Mapped[int]        = mapped_column(primary_key=True, index=True)
    quiz_id:        Mapped[int]        = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"))
    question:       Mapped[str]        = mapped_column(Text, nullable=False)
    option_a:       Mapped[str]        = mapped_column(String(500))
    option_b:       Mapped[str]        = mapped_column(String(500))
    option_c:       Mapped[str | None] = mapped_column(String(500))
    option_d:       Mapped[str | None] = mapped_column(String(500))
    correct_answer: Mapped[str]        = mapped_column(String(1))
    explanation:    Mapped[str | None] = mapped_column(Text)
    quiz = relationship("Quiz", back_populates="questions")

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id:           Mapped[int]      = mapped_column(primary_key=True, index=True)
    student_id:   Mapped[int]      = mapped_column(ForeignKey("students.id", ondelete="CASCADE"))
    quiz_id:      Mapped[int]      = mapped_column(ForeignKey("quizzes.id",  ondelete="CASCADE"))
    score:        Mapped[int]      = mapped_column(Integer, default=0)
    total:        Mapped[int]      = mapped_column(Integer, default=0)
    passed:       Mapped[bool]     = mapped_column(Boolean, default=False)
    attempted_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    quiz = relationship("Quiz", back_populates="attempts")
