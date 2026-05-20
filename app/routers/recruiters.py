from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.recruiter import Recruiter
from app.models.student import Student
from app.schemas.recruiter import RecruiterRegister, RecruiterProfile
from app.schemas.student import StudentPublicProfile
from app.auth import hash_password, get_current_recruiter

router = APIRouter(prefix="/recruiters", tags=["recruiters"])


@router.post("/register", response_model=RecruiterProfile, status_code=status.HTTP_201_CREATED)
def register(payload: RecruiterRegister, db: Session = Depends(get_db)):
    if db.query(Recruiter).filter(Recruiter.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    recruiter = Recruiter(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        company=payload.company,
        job_title=payload.job_title,
    )
    db.add(recruiter)
    db.commit()
    db.refresh(recruiter)
    return recruiter


@router.get("/me", response_model=RecruiterProfile)
def get_my_profile(current: Recruiter = Depends(get_current_recruiter)):
    return current


@router.get("/students", response_model=list[StudentPublicProfile])
def list_students(
    school: str | None = Query(None),
    field_of_study: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    _: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    """Browse visible student profiles. Supports filtering by school and field of study."""
    query = db.query(Student).filter(Student.is_visible == True)

    if school:
        query = query.filter(Student.school.ilike(f"%{school}%"))
    if field_of_study:
        query = query.filter(Student.field_of_study.ilike(f"%{field_of_study}%"))

    return query.offset(skip).limit(limit).all()


@router.get("/students/{student_id}", response_model=StudentPublicProfile)
def get_student(
    student_id: int,
    _: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.id == student_id, Student.is_visible == True).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return student
