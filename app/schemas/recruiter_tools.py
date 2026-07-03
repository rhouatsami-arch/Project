from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class ATSRequest(BaseModel):
    student_id:      UUID
    job_description: str
    requirements:    str | None = None


class ATSResult(BaseModel):
    student_id:       UUID
    full_name:        str
    cv_url:           str | None
    score:            float
    matched_keywords: list[str]
    missing_keywords: list[str]
    recommendation:   str


class InterviewCreate(BaseModel):
    student_id:   UUID
    job_title:    str | None = None
    scheduled_at: datetime
    duration_min: int        = 30
    meeting_link: str | None = None
    notes:        str | None = None


class InterviewUpdate(BaseModel):
    scheduled_at: datetime | None = None
    duration_min: int      | None = None
    meeting_link: str      | None = None
    notes:        str      | None = None
    status:       str      | None = None


class InterviewOut(BaseModel):
    id:           int
    student_id:   UUID
    job_title:    str | None
    scheduled_at: datetime
    duration_min: int
    meeting_link: str | None
    notes:        str | None
    status:       str
    ats_score:    int | None
    created_at:   datetime
    model_config  = {"from_attributes": True}
