from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class QuestionOut(BaseModel):
    id:          int
    question:    str
    option_a:    str
    option_b:    str
    option_c:    str | None
    option_d:    str | None
    model_config = {"from_attributes": True}


class QuizOut(BaseModel):
    id:          int
    title:       str
    description: str | None
    topic:       str | None
    difficulty:  str | None
    created_at:  datetime
    model_config = {"from_attributes": True}


class QuizDetail(QuizOut):
    questions: list[QuestionOut]
    model_config = {"from_attributes": True}


class AnswerItem(BaseModel):
    question_id: int
    answer:      str   # "a" | "b" | "c" | "d"


class QuizSubmit(BaseModel):
    answers: list[AnswerItem]


class AttemptOut(BaseModel):
    id:           int
    quiz_id:      int
    score:        int
    total:        int
    passed:       bool
    attempted_at: datetime
    model_config  = {"from_attributes": True}


class AttemptResult(AttemptOut):
    percentage: float
    feedback:   str
