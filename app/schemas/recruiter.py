from pydantic import BaseModel, EmailStr


class RecruiterRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    company: str | None = None
    job_title: str | None = None


class RecruiterProfile(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    company: str | None
    job_title: str | None

    model_config = {"from_attributes": True}
