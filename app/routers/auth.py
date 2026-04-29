from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.student import Student
from app.models.recruiter import Recruiter
from app.auth import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login for both students and recruiters. Returns a JWT bearer token."""
    user = db.query(Student).filter(Student.email == form.username).first()
    role = "student"

    if not user:
        user = db.query(Recruiter).filter(Recruiter.email == form.username).first()
        role = "recruiter"

    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token(user.email, role),
        "token_type": "bearer",
        "role": role,
    }
