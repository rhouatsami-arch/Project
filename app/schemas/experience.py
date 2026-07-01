import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.experience import ExperienceType


class ExperienceCreate(BaseModel):
    title:       str
    company:     str
    location:    Optional[str]          = None
    type:        ExperienceType         = ExperienceType.full_time
    description: Optional[str]          = None
    skills_used: Optional[str]          = None
    start_date:  datetime.datetime
    end_date:    Optional[datetime.datetime] = None
    is_current:  bool                   = False


class ExperienceUpdate(BaseModel):
    title:       Optional[str]          = None
    company:     Optional[str]          = None
    location:    Optional[str]          = None
    type:        Optional[ExperienceType]= None
    description: Optional[str]          = None
    skills_used: Optional[str]          = None
    start_date:  Optional[datetime.datetime] = None
    end_date:    Optional[datetime.datetime] = None
    is_current:  Optional[bool]         = None


class ExperienceOut(BaseModel):
    id:          int
    student_id:  str
    title:       str
    company:     str
    location:    Optional[str]
    type:        ExperienceType
    description: Optional[str]
    skills_used: Optional[str]
    start_date:  datetime.datetime
    end_date:    Optional[datetime.datetime]
    is_current:  bool
    created_at:  datetime.datetime
    model_config = {"from_attributes": True}
