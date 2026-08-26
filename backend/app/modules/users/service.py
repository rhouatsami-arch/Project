from sqlalchemy.orm import Session

from app.auth import hash_password
from app.models.recruitment import Recruiter, Student
from app.modules.cv.storage import delete_cv_file


class UserService:
    """CRUD helpers for student/candidate and recruiter profiles."""

    @staticmethod
    def update_student(student: Student, payload: dict) -> Student:
        for field, value in payload.items():
            setattr(student, field, value)
        return student

    @staticmethod
    def update_recruiter(recruiter: Recruiter, payload: dict) -> Recruiter:
        for field, value in payload.items():
            setattr(recruiter, field, value)
        return recruiter

    @staticmethod
    def delete_student(student: Student, db: Session) -> None:
        delete_cv_file(student.cv_path)
        db.delete(student)
        db.commit()

    @staticmethod
    def delete_recruiter(recruiter: Recruiter, db: Session) -> None:
        db.delete(recruiter)
        db.commit()

    @staticmethod
    def create_student(
        db: Session, data: dict, *, account_kind: str = "student"
    ) -> Student:
        student = Student(
            email=data["email"],
            hashed_password=hash_password(data["password"]),
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone=data.get("phone"),
            university=data.get("university"),
            field_of_study=data.get("field_of_study"),
            graduation_year=data.get("graduation_year"),
            skills=data.get("technical_skills"),
            technical_skills=data.get("technical_skills"),
            soft_skills=data.get("soft_skills"),
            internship_type=data.get("internship_type"),
            internship_duration=data.get("internship_duration"),
            account_kind=account_kind,
        )
        db.add(student)
        db.commit()
        db.refresh(student)
        return student

    @staticmethod
    def create_recruiter(db: Session, data: dict) -> Recruiter:
        recruiter = Recruiter(
            email=data["email"],
            hashed_password=hash_password(data["password"]),
            first_name=data["first_name"],
            last_name=data["last_name"],
            company_name=data["company_name"],
            phone=data.get("phone"),
        )
        db.add(recruiter)
        db.commit()
        db.refresh(recruiter)
        return recruiter
