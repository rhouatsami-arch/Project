from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime

class AdminRegister(BaseModel):
    email:      EmailStr
    password:   str
    first_name: str
    last_name:  str

class AdminOut(BaseModel):
    id:           UUID
    email:        str
    first_name:   str
    last_name:    str
    is_superadmin:bool
    is_active:    bool
    created_at:   datetime
    model_config  = {"from_attributes": True}

class AdminStats(BaseModel):
    total_students:    int
    total_recruiters:  int
    total_candidates:  int
    total_jobs:        int
    total_applications:int
    total_interviews:  int
    total_quizzes:     int
