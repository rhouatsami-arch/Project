from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.recruitment import StudentOut


class CvUploadOut(BaseModel):
    cv_filename: str
    extracted_char_count: int
    extracted_text_preview: str = Field(
        description="First 500 characters of raw extracted text"
    )
    skills_detected: list[str]
    profile: StudentOut


class CvExtractedTextOut(BaseModel):
    filename: str | None
    extracted_at: datetime | None
    char_count: int
    raw_text: str = Field(description="Full raw text extracted from the CV file")
    skills_detected: list[str]
