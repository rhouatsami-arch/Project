from pydantic import BaseModel, EmailStr


class StudentRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class StudentProfileUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    school: str | None = None
    field_of_study: str | None = None
    graduation_year: int | None = None
    bio: str | None = None
    skills: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    is_visible: bool | None = None


class StudentPublicProfile(BaseModel):
    id: int
    first_name: str
    last_name: str
    school: str | None
    field_of_study: str | None
    graduation_year: int | None
    bio: str | None
    skills: str | None
    linkedin_url: str | None
    github_url: str | None

    model_config = {"from_attributes": True}


class StudentPrivateProfile(StudentPublicProfile):
    email: str
    is_visible: bool

    model_config = {"from_attributes": True}
