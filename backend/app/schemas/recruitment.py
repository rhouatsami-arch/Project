from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.recruitment import ApplicationStatus, JobStatus


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class StudentRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str
    phone: str | None = None
    university: str | None = None
    field_of_study: str | None = None
    graduation_year: int | None = None
    technical_skills: str | None = None
    soft_skills: str | None = None


class StudentUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    university: str | None = None
    field_of_study: str | None = None
    graduation_year: int | None = None
    bio: str | None = None
    skills: str | None = None
    technical_skills: str | None = None
    soft_skills: str | None = None
    experiences: str | None = None
    projects: str | None = None
    certifications: str | None = None
    languages: str | None = None


class StudentOut(BaseModel):
    id: UUID
    email: str
    first_name: str
    last_name: str
    phone: str | None
    university: str | None
    field_of_study: str | None
    graduation_year: int | None
    bio: str | None
    skills: str | None
    technical_skills: str | None
    soft_skills: str | None
    experiences: str | None
    projects: str | None
    certifications: str | None
    languages: str | None
    cv_filename: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RecruiterRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str
    company_name: str
    phone: str | None = None


class RecruiterUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    company_name: str | None = None
    phone: str | None = None


class RecruiterOut(BaseModel):
    id: UUID
    email: str
    first_name: str
    last_name: str
    company_name: str
    phone: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class JobCreate(BaseModel):
    title: str
    description: str
    required_skills: str | None = None
    location: str | None = None
    employment_type: str | None = "full_time"


class JobUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    required_skills: str | None = None
    location: str | None = None
    employment_type: str | None = None
    status: JobStatus | None = None


class JobOut(BaseModel):
    id: int
    recruiter_id: UUID
    title: str
    description: str
    required_skills: str | None
    location: str | None
    employment_type: str | None
    status: JobStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class ApplicationCreate(BaseModel):
    cover_letter: str | None = None


class ApplicationOut(BaseModel):
    id: int
    job_id: int
    student_id: UUID
    cover_letter: str | None
    status: ApplicationStatus
    match_score: int
    interview_message: str | None
    interview_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CandidateOut(BaseModel):
    application_id: int
    student_id: UUID
    full_name: str
    email: str
    phone: str | None
    university: str | None
    field_of_study: str | None
    skills: str | None
    technical_skills: str | None
    soft_skills: str | None
    experiences: str | None
    projects: str | None
    certifications: str | None
    languages: str | None
    cv_filename: str | None
    application_status: ApplicationStatus
    match_score: int


class InterviewInvite(BaseModel):
    interview_at: datetime
    message: str | None = None


class SavedJobOut(BaseModel):
    id: int
    job: JobOut
    created_at: datetime

    model_config = {"from_attributes": True}
