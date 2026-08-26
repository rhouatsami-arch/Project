from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    computed_field,
    model_validator,
)

from app.models.recruitment import (
    INTERNSHIP_DURATION_LABELS,
    ApplicationStatus,
    InternshipDurationType,
    JobStatus,
    parse_internship_duration_type,
)


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
    internship_type: str | None = None
    internship_duration: str | None = None


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
    internship_type: str | None = None
    internship_duration: str | None = None


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
    internship_type: str | None
    internship_duration: str | None
    account_kind: str = "student"
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


class InternshipApplicationCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "internship_duration": "observation",
                "cover_letter": "I am interested in this internship opportunity.",
            }
        }
    )

    internship_duration: InternshipDurationType | None = Field(
        default=None,
        description=(
            "observation = 1 to 2 weeks, operational = 1 to 3 months, "
            "functional = 4 to 6 months"
        ),
    )
    internship_type: InternshipDurationType | None = Field(
        default=None,
        description="Alias for internship_duration",
    )
    cover_letter: str | None = None

    @model_validator(mode="after")
    def resolve_internship_duration(self):
        raw = self.internship_duration or self.internship_type
        if raw is None:
            raise ValueError("internship_duration is required")
        self.internship_duration = parse_internship_duration_type(raw)
        self.internship_type = self.internship_duration
        return self


class ApplicationOut(BaseModel):
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


class StudentDashboardApplicationOut(BaseModel):
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


class SavedJobOut(BaseModel):
    id: int
    job: JobOut
    created_at: datetime

    model_config = {"from_attributes": True}


class StudentDashboardOut(BaseModel):
    total_applications: int
    interview_invites: int
    saved_jobs_count: int
    applications: list[StudentDashboardApplicationOut]
    saved_jobs: list[SavedJobOut]

    model_config = {"from_attributes": True}


class RecruiterRecentApplicationOut(BaseModel):
    application_id: int
    job_id: int
    job_title: str
    candidate_name: str
    candidate_email: str
    status: str
    match_score: int
    created_at: str


class RecruiterUpcomingMeetingOut(BaseModel):
    meeting_id: int
    job_id: int
    scheduled_at: str
    status: str
    location: str | None
    candidate_name: str


class RecruiterDashboardOut(BaseModel):
    open_jobs: int
    closed_jobs: int
    total_applications: int
    applied_count: int
    shortlisted_count: int
    interview_count: int
    rejected_count: int
    hired_count: int
    upcoming_meetings: int
    average_match_score: int
    recent_applications: list[RecruiterRecentApplicationOut]
    upcoming_meeting_list: list[RecruiterUpcomingMeetingOut]
