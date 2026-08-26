import base64
import hashlib
import hmac
import json
import os
import secrets
from datetime import UTC, datetime, timedelta
from typing import Literal

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.platform import Admin
from app.models.recruitment import Recruiter, Student
from app.modules.auth.session_service import ACCESS_COOKIE

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY") or "development-secret-change-me"

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
LOGIN_CHALLENGE_EXPIRE_MINUTES = int(os.getenv("LOGIN_CHALLENGE_EXPIRE_MINUTES", "5"))
OAUTH_STATE_EXPIRE_MINUTES = int(os.getenv("OAUTH_STATE_EXPIRE_MINUTES", "10"))

Role = Literal["student", "candidate", "recruiter", "admin"]
TokenType = Literal[
    "access", "refresh", "login_challenge", "oauth_state", "calendar_oauth_state"
]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 260_000)
    return f"pbkdf2_sha256${salt}${base64.urlsafe_b64encode(digest).decode()}"


def verify_password(plain: str, hashed: str) -> bool:
    try:
        algorithm, salt, expected = hashed.split("$", 2)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    digest = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt.encode(), 260_000)
    actual = base64.urlsafe_b64encode(digest).decode()
    return hmac.compare_digest(actual, expected)


def _sign(value: str) -> str:
    digest = hmac.new(SECRET_KEY.encode(), value.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode()


def _create_signed_token(payload: dict) -> str:
    body = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(",", ":")).encode()
    ).decode()
    return f"{body}.{_sign(body)}"


def create_access_token(subject: str, role: Role) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_signed_token(
        {
            "sub": subject,
            "role": role,
            "typ": "access",
            "exp": int(expires_at.timestamp()),
        }
    )


def create_refresh_token(subject: str, role: Role) -> str:
    expires_at = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return _create_signed_token(
        {
            "sub": subject,
            "role": role,
            "typ": "refresh",
            "jti": secrets.token_urlsafe(16),
            "exp": int(expires_at.timestamp()),
        }
    )


def create_login_challenge(subject: str, role: Role) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=LOGIN_CHALLENGE_EXPIRE_MINUTES)
    return _create_signed_token(
        {
            "sub": subject,
            "role": role,
            "typ": "login_challenge",
            "exp": int(expires_at.timestamp()),
        }
    )


def create_oauth_state_token(provider: str, role: Role) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=OAUTH_STATE_EXPIRE_MINUTES)
    return _create_signed_token(
        {
            "provider": provider,
            "role": role,
            "typ": "oauth_state",
            "nonce": secrets.token_urlsafe(16),
            "exp": int(expires_at.timestamp()),
        }
    )


def decode_oauth_state_token(state: str, *, expected_provider: str) -> dict:
    payload = decode_token(state, expected_type="oauth_state")
    if payload.get("provider") != expected_provider:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")
    return payload


def create_calendar_oauth_state_token(recruiter_email: str) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=OAUTH_STATE_EXPIRE_MINUTES)
    return _create_signed_token(
        {
            "sub": recruiter_email,
            "typ": "calendar_oauth_state",
            "nonce": secrets.token_urlsafe(16),
            "exp": int(expires_at.timestamp()),
        }
    )


def decode_calendar_oauth_state_token(state: str) -> str:
    payload = decode_token(state, expected_type="calendar_oauth_state")
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=400, detail="Invalid calendar OAuth state")
    return email


def decode_token(token: str, *, expected_type: TokenType | None = None) -> dict:
    try:
        body, signature = token.rsplit(".", 1)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        ) from exc
    if not hmac.compare_digest(_sign(body), signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        ) from None
    try:
        payload = json.loads(base64.urlsafe_b64decode(body.encode()).decode())
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        ) from exc
    if payload.get("exp", 0) < int(datetime.now(UTC).timestamp()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )
    if expected_type and payload.get("typ") != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
        )
    return payload


def _extract_bearer_token(
    request: Request, header_token: str | None = None
) -> str | None:
    if header_token:
        return header_token
    cookie_token = request.cookies.get(ACCESS_COOKIE)
    if cookie_token:
        return cookie_token
    return None


def get_authenticated_actor(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    resolved = _extract_bearer_token(request, token)
    if not resolved:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(resolved, expected_type="access")
    email = payload.get("sub")
    role = payload.get("role")
    if role in {"student", "candidate"}:
        user = db.query(Student).filter(Student.email == email).first()
    elif role == "recruiter":
        user = db.query(Recruiter).filter(Recruiter.email == email).first()
    elif role == "admin":
        user = db.query(Admin).filter(Admin.email == email).first()
    else:
        raise HTTPException(status_code=403, detail="Unsupported role")
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return role, user


def get_current_student(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Student:
    resolved = _extract_bearer_token(request, token)
    if not resolved:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(resolved, expected_type="access")
    if payload.get("role") != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Student account required"
        )
    student = db.query(Student).filter(Student.email == payload.get("sub")).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Student not found"
        )
    return student


def get_current_candidate(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Student:
    resolved = _extract_bearer_token(request, token)
    if not resolved:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(resolved, expected_type="access")
    if payload.get("role") != "candidate":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Candidate account required"
        )
    student = db.query(Student).filter(Student.email == payload.get("sub")).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Candidate not found"
        )
    return student


def get_current_recruiter(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Recruiter:
    resolved = _extract_bearer_token(request, token)
    if not resolved:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(resolved, expected_type="access")
    if payload.get("role") != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Recruiter account required"
        )
    recruiter = (
        db.query(Recruiter).filter(Recruiter.email == payload.get("sub")).first()
    )
    if not recruiter:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Recruiter not found"
        )
    return recruiter


def get_current_admin(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Admin:
    resolved = _extract_bearer_token(request, token)
    if not resolved:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_token(resolved, expected_type="access")
    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin account required"
        )
    admin = db.query(Admin).filter(Admin.email == payload.get("sub")).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found"
        )
    return admin
