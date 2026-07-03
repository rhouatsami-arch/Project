from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.candidate import CandidateStatus, AppStatus


class CandidateRegister(BaseModel):
    email:      EmailStr
    password:   str
    first_name: str
    last_name:  str

class CandidateUpdate(BaseModel):
    first_name:  str | None = None
    last_name:   str | None = None
    phone:       str | None = None
    bio:         str | None = None
    skills:      str | None = None
    location:    str | None = None
    linkedin_url:str | None = None
    github_url:  str | None = None
    is_visible:  bool | None = None
    status:      CandidateStatus | None = None

class DocumentOut(BaseModel):
    id:        int
    name:      str
    type:      str
    file_url:  str
    created_at:datetime
    model_config = {"from_attributes": True}

class ApplicationCreate(BaseModel):
    job_id:       int
    cover_letter: str | None = None

class ApplicationOut(BaseModel):
    id:           int
    job_id:       int
    status:       AppStatus
    cover_letter: str | None
    applied_at:   datetime
    model_config  = {"from_attributes": True}

class FavoriteOut(BaseModel):
    id:       int
    job_id:   int
    saved_at: datetime
    model_config = {"from_attributes": True}

class CandidateProfile(BaseModel):
    id:          UUID
    email:       str
    first_name:  str
    last_name:   str
    phone:       str | None
    bio:         str | None
    skills:      str | None
    location:    str | None
    linkedin_url:str | None
    github_url:  str | None
    cv_url:      str | None
    is_visible:  bool
    status:      CandidateStatus | None
    created_at:  datetime
    model_config = {"from_attributes": True}

class CandidateStats(BaseModel):
    total_applications: int
    pending:            int
    accepted:           int
    rejected:           int
    total_favorites:    int
    total_documents:    int
