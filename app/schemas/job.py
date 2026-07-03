import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.job import JobType, JobStatus

class JobCreate(BaseModel):
    title:        str
    description:  str
    requirements: Optional[str] = None
    location:     Optional[str] = None
    type:         JobType       = JobType.full_time

class JobUpdate(BaseModel):
    title:        Optional[str]       = None
    description:  Optional[str]       = None
    requirements: Optional[str]       = None
    location:     Optional[str]       = None
    type:         Optional[JobType]   = None
    status:       Optional[JobStatus] = None
    is_active:    Optional[bool]      = None

class JobOut(BaseModel):
    id:           int
    recruiter_id: uuid.UUID
    title:        str
    description:  str
    requirements: Optional[str] = None
    location:     Optional[str] = None
    type:         JobType
    status:       JobStatus
    is_active:    bool
    created_at:   datetime.datetime
    model_config  = {"from_attributes": True}

import uuid
