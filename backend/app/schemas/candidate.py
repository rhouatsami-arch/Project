from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, computed_field

from app.models.recruitment import (
    INTERNSHIP_DURATION_LABELS,
    ApplicationStatus,
    InternshipDurationType,
)
from app.schemas.matching import ScoreBreakdownOut


class Candidate(BaseModel):
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
    internship_type: str | None
    internship_duration: str | None
    account_kind: str = "candidate"
    cv_filename: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class CandidateRegister(BaseModel):
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
    internship_type: str | None = None
    internship_duration: str | None = None


class CandidateUpdate(BaseModel):
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
    internship_type: str | None = None
    internship_duration: str | None = None


class CandidateOut(Candidate):
    application_id: int
    application_status: ApplicationStatus
    match_score: int
    rank: int | None = None
    rank_label: str | None = None
    breakdown: ScoreBreakdownOut | None = None
    explanation: str | None = None


class InterviewInvite(BaseModel):
    interview_at: datetime
    message: str | None = None


class CandidateApplicationOut(BaseModel):
    id: int
    job_id: int
    student_id: UUID
    cover_letter: str | None
    internship_type: InternshipDurationType | None
    status: ApplicationStatus
    match_score: int
    interview_message: str | None
    interview_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}

    @computed_field
    @property
    def internship_duration_label(self) -> str | None:
        if self.internship_type is None:
            return None
        return INTERNSHIP_DURATION_LABELS.get(self.internship_type)


class CandidateDashboardApplicationOut(BaseModel):
    id: int
    job_id: int
    job_title: str
    job_location: str | None
    job_employment_type: str | None
    cover_letter: str | None
    internship_type: InternshipDurationType | None = None
    status: ApplicationStatus
    match_score: int
    interview_message: str | None
    interview_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class JobSummary(BaseModel):
    id: int
    title: str
    location: str | None

    model_config = {"from_attributes": True}


class CandidateSavedJobOut(BaseModel):
    id: int
    job: JobSummary
    created_at: datetime

    model_config = {"from_attributes": True}


class CandidateDashboardOut(BaseModel):
    total_applications: int
    interview_invites: int
    saved_jobs_count: int
    applications: list[CandidateDashboardApplicationOut]
    saved_jobs: list[CandidateSavedJobOut]

    model_config = {"from_attributes": True}
