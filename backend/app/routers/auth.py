from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models.recruitment import Recruiter, Student
from app.schemas.recruitment import RecruiterOut, RecruiterRegister, StudentOut, StudentRegister, TokenOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/students/register", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
def register_student(payload: StudentRegister, db: Session = Depends(get_db)):
    if _email_exists(payload.email, db):
        raise HTTPException(status_code=409, detail="Email already registered")
    student = Student(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone=payload.phone,
        university=payload.university,
        field_of_study=payload.field_of_study,
        graduation_year=payload.graduation_year,
        skills=payload.technical_skills,
        technical_skills=payload.technical_skills,
        soft_skills=payload.soft_skills,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.post("/recruiters/register", response_model=RecruiterOut, status_code=status.HTTP_201_CREATED)
def register_recruiter(payload: RecruiterRegister, db: Session = Depends(get_db)):
    if _email_exists(payload.email, db):
        raise HTTPException(status_code=409, detail="Email already registered")
    recruiter = Recruiter(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        company_name=payload.company_name,
        phone=payload.phone,
    )
    db.add(recruiter)
    db.commit()
    db.refresh(recruiter)
    return recruiter


@router.post("/login", response_model=TokenOut)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.email == form.username).first()
    if student and verify_password(form.password, student.hashed_password):
        return {"access_token": create_access_token(student.email, "student"), "role": "student"}

    recruiter = db.query(Recruiter).filter(Recruiter.email == form.username).first()
    if recruiter and verify_password(form.password, recruiter.hashed_password):
        return {"access_token": create_access_token(recruiter.email, "recruiter"), "role": "recruiter"}

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")


def _email_exists(email: str, db: Session) -> bool:
    return bool(
        db.query(Student).filter(Student.email == email).first()
        or db.query(Recruiter).filter(Recruiter.email == email).first()
    )
