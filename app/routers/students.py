import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.student import Student
from app.schemas.student import StudentRegister, StudentProfileUpdate, StudentPrivateProfile
from app.auth import hash_password, get_current_student

router = APIRouter(prefix="/students", tags=["students"])


@router.post("/register", response_model=StudentPrivateProfile, status_code=status.HTTP_201_CREATED)
def register(payload: StudentRegister, db: Session = Depends(get_db)):
    if db.query(Student).filter(Student.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    student = Student(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.get("/me", response_model=StudentPrivateProfile)
def get_my_profile(current: Student = Depends(get_current_student)):
    return current


@router.patch("/me", response_model=StudentPrivateProfile)
def update_my_profile(
    payload: StudentProfileUpdate,
    current: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current, field, value)
    db.commit()
    db.refresh(current)
    return current


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_my_account(current: Student = Depends(get_current_student), db: Session = Depends(get_db)):
    db.delete(current)
    db.commit()


@router.post("/me/cv", status_code=status.HTTP_200_OK)
async def upload_cv(
    cv: UploadFile = File(...),
    current: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    # ── Validate extension ──
    ext = cv.filename.rsplit(".", 1)[-1].lower()
    if ext not in {"pdf", "doc", "docx"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, DOC, DOCX files are allowed"
        )

    # ── Validate size (5 MB max) ──
    contents = await cv.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum size is 5MB"
        )

    # ── Save file ──
    os.makedirs("uploads/cvs", exist_ok=True)
    filepath = f"uploads/cvs/student_{current.id}_{cv.filename}"
    with open(filepath, "wb") as f:
        f.write(contents)

    # ── Persist path in DB ──
    current.cv_url = filepath
    db.commit()
    db.refresh(current)

    return {
        "message": "CV uploaded successfully",
        "cv_url": filepath
    }
