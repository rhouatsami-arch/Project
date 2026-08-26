from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class AdminOut(BaseModel):
    id: UUID
    email: str
    first_name: str
    last_name: str

    model_config = {"from_attributes": True}


class AdminRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str


class AuditLogOut(BaseModel):
    id: int
    actor_email: str
    actor_role: str
    action: str
    action_label: str | None = None
    resource: str | None
    details: str | None
    created_at: str

    model_config = {"from_attributes": True}


class AdminDashboardOut(BaseModel):
    total_students: int
    total_candidates: int
    total_recruiters: int
    total_jobs: int
    total_applications: int
    total_meetings: int
    total_recommendations: int
    recent_audit_logs: list[AuditLogOut]


class AdminApplicantOut(BaseModel):
    id: UUID
    email: str
    first_name: str
    last_name: str
    university: str | None = None
    field_of_study: str | None = None
    account_kind: str
    created_at: str


class AdminRecruiterOut(BaseModel):
    id: UUID
    email: str
    first_name: str
    last_name: str
    company_name: str
    phone: str | None = None
    created_at: str


class AdminCreateStudent(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str
    phone: str | None = None
    university: str | None = None
    field_of_study: str | None = None
    internship_type: str | None = None
    internship_duration: str | None = None


class AdminCreateCandidate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str
    phone: str | None = None
    university: str | None = None
    field_of_study: str | None = None


class AdminCreateRecruiter(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str
    company_name: str
    phone: str | None = None


class MeetingOut(BaseModel):
    id: int
    application_id: int
    job_id: int
    scheduled_at: str
    location: str | None
    notes: str | None
    status: str
    slot_id: int | None = None
    updated_at: str | None = None
    google_event_link: str | None = None
    google_meet_link: str | None = None

    model_config = {"from_attributes": True}


class GoogleCalendarStatusOut(BaseModel):
    configured: bool
    connected: bool
    google_email: str | None = None


class MeetingCreate(BaseModel):
    application_id: int
    scheduled_at: str
    location: str | None = None
    notes: str | None = None


class MeetingPropose(BaseModel):
    application_id: int
    slot_id: int | None = None
    location: str | None = None
    notes: str | None = None


class MeetingReschedule(BaseModel):
    scheduled_at: str | None = None
    slot_id: int | None = None
    location: str | None = None
    notes: str | None = None


class InterviewSlotCreate(BaseModel):
    starts_at: str
    ends_at: str


class InterviewSlotOut(BaseModel):
    id: int
    starts_at: str
    ends_at: str
    is_booked: bool

    model_config = {"from_attributes": True}


class AvailabilityCreate(BaseModel):
    starts_at: str
    ends_at: str


class AvailabilityOut(BaseModel):
    id: int
    starts_at: str
    ends_at: str

    model_config = {"from_attributes": True}


class NotificationOut(BaseModel):
    id: int
    type: str
    title: str
    message: str
    is_read: bool
    created_at: str

    model_config = {"from_attributes": True}


class RecommendationHistoryOut(BaseModel):
    id: int
    job_id: int
    compatibility_score: int
    explanation: str | None
    created_at: str

    model_config = {"from_attributes": True}
