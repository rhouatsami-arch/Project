import os
import hashlib
import base64
from datetime import datetime, timedelta, timezone
from typing import Literal
from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.student import Student
from app.models.recruiter import Recruiter

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def _prehash(password: str) -> str:
    """SHA-256 pre-hash keeps input under bcrypt's 72-byte limit."""
    digest = hashlib.sha256(password.encode()).digest()
    return base64.b64encode(digest).decode()


def hash_password(password: str) -> str:
    return pwd_context.hash(_prehash(password))


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(_prehash(plain), hashed)


def create_access_token(subject: str, role: Literal["student", "recruiter", "candidate"]) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": subject, "role": role, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


def get_current_student(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Student:
    payload = _decode_token(token)
    if payload.get("role") != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a student account")
    student = db.query(Student).filter(Student.email == payload["sub"]).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Student not found")
    return student


def get_current_recruiter(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Recruiter:
    payload = _decode_token(token)
    if payload.get("role") != "recruiter":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a recruiter account")
    recruiter = db.query(Recruiter).filter(Recruiter.email == payload["sub"]).first()
    if not recruiter:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Recruiter not found")
    return recruiter


def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    from app.models.admin import Admin
    payload = _decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not an admin account")
    if not (admin := db.query(Admin).filter(Admin.email == payload["sub"]).first()):
        raise HTTPException(status_code=401, detail="Admin not found")
    if not admin.is_active:
        raise HTTPException(status_code=403, detail="Admin account disabled")
    return admin
