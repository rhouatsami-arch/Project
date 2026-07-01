import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.models.cv import CVStatus


class CVOut(BaseModel):
    id:           int
    filename:     str
    file_size:    int
    file_ext:     str
    status:       CVStatus
    is_current:   bool
    uploaded_at:  datetime.datetime
    processed_at: Optional[datetime.datetime] = None
    model_config  = {"from_attributes": True}


class CVExtractedData(BaseModel):
    emails:           List[str]
    phones:           List[str]
    urls:             List[str]
    skills_detected:  List[str]
    word_count:       int
    raw_text_preview: str


class CVDetailOut(CVOut):
    extracted: Optional[CVExtractedData] = None
