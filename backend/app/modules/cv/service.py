from dataclasses import dataclass

from app.models.recruitment import Student
from app.modules.cv.extraction import extract_raw_text
from app.modules.cv.skills import extract_skills_from_text
from app.modules.cv.storage import delete_cv_file, save_cv_file
from app.utils.datetime import utc_now


@dataclass
class CvUploadResult:
    filename: str
    path: str
    raw_text: str
    skills: list[str]
    char_count: int


class CvService:
    @staticmethod
    def upload(student: Student, filename: str, contents: bytes) -> CvUploadResult:
        delete_cv_file(student.cv_path)
        path = save_cv_file(str(student.id), filename, contents)
        raw_text = extract_raw_text(filename, contents)
        skills = extract_skills_from_text(raw_text)

        student.cv_filename = filename
        student.cv_path = path
        student.cv_extracted_text = raw_text or None
        student.cv_extracted_at = utc_now() if raw_text else None

        existing = {
            s.strip()
            for s in (student.technical_skills or student.skills or "").split(",")
            if s.strip()
        }
        merged = sorted(existing | set(skills))
        if merged:
            student.technical_skills = ", ".join(merged)
            student.skills = student.technical_skills

        return CvUploadResult(
            filename=filename,
            path=path,
            raw_text=raw_text,
            skills=skills,
            char_count=len(raw_text),
        )

    @staticmethod
    def delete(student: Student) -> None:
        delete_cv_file(student.cv_path)
        student.cv_filename = None
        student.cv_path = None
        student.cv_extracted_text = None
        student.cv_extracted_at = None

    @staticmethod
    def get_extracted(student: Student) -> dict:
        raw = student.cv_extracted_text or ""
        return {
            "filename": student.cv_filename,
            "extracted_at": student.cv_extracted_at,
            "char_count": len(raw),
            "raw_text": raw,
            "skills_detected": extract_skills_from_text(raw) if raw else [],
        }
