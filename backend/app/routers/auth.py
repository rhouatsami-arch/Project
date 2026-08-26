import os
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import (
    create_login_challenge,
    decode_token,
    get_authenticated_actor,
    hash_password,
    verify_password,
)
from app.database import get_db
from app.models.platform import Admin
from app.models.recruitment import Recruiter, Student
from app.modules.auth.oauth_service import (
    build_authorize_url,
    exchange_code,
    list_providers,
    resolve_oauth_user,
)
from app.modules.auth.session_service import (
    REFRESH_COOKIE,
    clear_auth_cookies,
    set_auth_cookies,
)
from app.modules.auth.token_service import (
    issue_token_pair,
    refresh_tokens,
    revoke_refresh_token,
)
from app.modules.auth.totp_service import (
    enable_totp,
    is_mfa_enabled,
    setup_totp,
    verify_totp,
)
from app.modules.platform.audit import AuditAction, record_audit
from app.schemas.auth_extended import (
    AuthFeaturesOut,
    LoginResponse,
    MfaEnableRequest,
    MfaSetupOut,
    MfaVerifyLoginRequest,
    OAuthProviderOut,
    OAuthProvidersOut,
    RefreshRequest,
    TokenPairOut,
)
from app.schemas.candidate import Candidate, CandidateRegister
from app.schemas.platform import AdminOut, AdminRegister
from app.schemas.recruitment import (
    RecruiterOut,
    RecruiterRegister,
    StudentOut,
    StudentRegister,
)
from app.utils.email import normalize_email

router = APIRouter(prefix="/auth", tags=["auth"])

FRONTEND_OAUTH_CALLBACK = os.getenv(
    "FRONTEND_OAUTH_CALLBACK", "http://127.0.0.1:3000/login/oauth/callback"
)


def _login_response(
    response: Response,
    *,
    email: str,
    role: str,
    db: Session,
) -> LoginResponse:
    if is_mfa_enabled(db, email):
        challenge = create_login_challenge(email, role)  # type: ignore[arg-type]
        return LoginResponse(requires_2fa=True, login_challenge=challenge, role=role)

    pair = issue_token_pair(db, email=email, role=role)
    set_auth_cookies(
        response,
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
    )
    return LoginResponse(
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
        role=pair.role,
    )


def _finalize_login_response(response: Response, pair: TokenPairOut) -> LoginResponse:
    set_auth_cookies(
        response,
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
    )
    return LoginResponse(
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
        role=pair.role,
    )


@router.get("/features", response_model=AuthFeaturesOut)
def auth_features():
    return AuthFeaturesOut(
        oidc_enterprise_sso=bool(
            os.getenv("OIDC_ISSUER") and os.getenv("OIDC_CLIENT_ID")
        ),
    )


@router.get("/oauth/providers", response_model=OAuthProvidersOut)
def oauth_providers():
    return OAuthProvidersOut(
        providers=[OAuthProviderOut(**item) for item in list_providers()]
    )


@router.get("/oauth/{provider}/authorize")
def oauth_authorize(
    provider: str,
    role: Literal["student", "candidate", "recruiter", "admin"] = Query("student"),
):
    try:
        url = build_authorize_url(provider, role)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return RedirectResponse(url=url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    response: Response,
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
):
    try:
        profile = await exchange_code(provider, code, state)
        state_payload = decode_token(state, expected_type="oauth_state")
        role = state_payload.get("role", "student")
        email, role, _user_id = resolve_oauth_user(db, profile, role)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    record_audit(
        db,
        actor_email=email,
        actor_role=role,
        action=AuditAction.LOGIN,
        details=f"oauth:{provider}",
    )
    db.commit()

    if is_mfa_enabled(db, email):
        challenge = create_login_challenge(email, role)  # type: ignore[arg-type]
        redirect = (
            f"{FRONTEND_OAUTH_CALLBACK}?requires_2fa=1"
            f"&login_challenge={challenge}&role={role}"
        )
        return RedirectResponse(
            url=redirect,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )

    pair = issue_token_pair(db, email=email, role=role)
    db.commit()
    set_auth_cookies(
        response,
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
    )
    redirect = (
        f"{FRONTEND_OAUTH_CALLBACK}?access_token={pair.access_token}"
        f"&refresh_token={pair.refresh_token}&role={pair.role}"
    )
    return RedirectResponse(
        url=redirect,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )


@router.post("/refresh", response_model=TokenPairOut)
def refresh_access_token(
    request: Request,
    response: Response,
    payload: RefreshRequest | None = None,
    db: Session = Depends(get_db),
):
    raw_refresh = (payload.refresh_token if payload else None) or request.cookies.get(
        REFRESH_COOKIE
    )
    if not raw_refresh:
        raise HTTPException(status_code=401, detail="Refresh token required")
    try:
        pair = refresh_tokens(db, raw_refresh)
        db.commit()
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    set_auth_cookies(
        response,
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
    )
    return pair


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    payload: RefreshRequest | None = None,
    db: Session = Depends(get_db),
):
    raw_refresh = (payload.refresh_token if payload else None) or request.cookies.get(
        REFRESH_COOKIE
    )
    if raw_refresh:
        revoke_refresh_token(db, raw_refresh)
        db.commit()
    clear_auth_cookies(response)


@router.post("/2fa/setup", response_model=MfaSetupOut)
def mfa_setup(
    db: Session = Depends(get_db),
    actor: tuple[str, object] = Depends(get_authenticated_actor),
):
    role, user = actor
    secret, uri = setup_totp(
        db,
        user_role=role,
        user_id=user.id,  # type: ignore[attr-defined]
        email=user.email,  # type: ignore[attr-defined]
    )
    db.commit()
    return MfaSetupOut(secret=secret, provisioning_uri=uri)


@router.post("/2fa/enable")
def mfa_enable(
    payload: MfaEnableRequest,
    db: Session = Depends(get_db),
    actor: tuple[str, object] = Depends(get_authenticated_actor),
):
    role, user = actor
    try:
        enable_totp(
            db,
            user_role=role,
            user_id=user.id,  # type: ignore[attr-defined]
            code=payload.totp_code,
        )
        db.commit()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"enabled": True}


@router.post("/2fa/verify-login", response_model=LoginResponse)
def verify_login_2fa(
    payload: MfaVerifyLoginRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    challenge_payload = decode_token(
        payload.login_challenge,
        expected_type="login_challenge",
    )
    email = challenge_payload.get("sub")
    role = challenge_payload.get("role")
    if not email or not role:
        raise HTTPException(status_code=400, detail="Invalid login challenge")
    if not verify_totp(db, email, payload.totp_code):
        raise HTTPException(status_code=401, detail="Invalid 2FA code")
    pair = issue_token_pair(db, email=email, role=role)
    db.commit()
    return _finalize_login_response(response, pair)


@router.post(
    "/students/register", response_model=StudentOut, status_code=status.HTTP_201_CREATED
)
def register_student(payload: StudentRegister, db: Session = Depends(get_db)):
    email = normalize_email(str(payload.email))
    if _email_exists(email, db):
        raise HTTPException(
            status_code=409,
            detail="Email already registered. Sign in with your password instead.",
        )
    student = Student(
        email=email,
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
        internship_type=payload.internship_type,
        internship_duration=payload.internship_duration,
        account_kind="student",
    )
    db.add(student)
    record_audit(
        db,
        actor_email=student.email,
        actor_role="student",
        action=AuditAction.REGISTER_STUDENT,
        resource=str(student.id),
    )
    db.commit()
    db.refresh(student)
    return student


@router.post(
    "/candidates/register",
    response_model=Candidate,
    status_code=status.HTTP_201_CREATED,
)
def register_candidate(payload: CandidateRegister, db: Session = Depends(get_db)):
    email = normalize_email(str(payload.email))
    existing_student = _find_student_by_email(db, email)
    if existing_student:
        if existing_student.account_kind == "candidate":
            raise HTTPException(
                status_code=409,
                detail="Email already registered. Sign in with your password instead.",
            )
        if verify_password(payload.password, existing_student.hashed_password):
            existing_student.account_kind = "candidate"
            existing_student.first_name = payload.first_name
            existing_student.last_name = payload.last_name
            existing_student.phone = payload.phone
            existing_student.university = payload.university
            existing_student.field_of_study = payload.field_of_study
            existing_student.graduation_year = payload.graduation_year
            if payload.technical_skills:
                existing_student.technical_skills = payload.technical_skills
                existing_student.skills = payload.technical_skills
            if payload.soft_skills:
                existing_student.soft_skills = payload.soft_skills
            existing_student.internship_type = None
            existing_student.internship_duration = None
            record_audit(
                db,
                actor_email=existing_student.email,
                actor_role="candidate",
                action=AuditAction.REGISTER_CANDIDATE,
                resource=str(existing_student.id),
                details="upgraded_from_student",
            )
            db.commit()
            db.refresh(existing_student)
            return existing_student
        raise HTTPException(
            status_code=409,
            detail="Email already registered. Sign in with your password instead.",
        )
    if _email_exists(email, db):
        raise HTTPException(
            status_code=409,
            detail="Email already registered. Sign in with your password instead.",
        )
    candidate = Student(
        email=email,
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
        internship_type=None,
        internship_duration=None,
        account_kind="candidate",
    )
    db.add(candidate)
    record_audit(
        db,
        actor_email=candidate.email,
        actor_role="candidate",
        action=AuditAction.REGISTER_CANDIDATE,
        resource=str(candidate.id),
    )
    db.commit()
    db.refresh(candidate)
    return candidate


@router.post(
    "/recruiters/register",
    response_model=RecruiterOut,
    status_code=status.HTTP_201_CREATED,
)
def register_recruiter(payload: RecruiterRegister, db: Session = Depends(get_db)):
    email = normalize_email(str(payload.email))
    if _email_exists(email, db):
        raise HTTPException(
            status_code=409,
            detail="Email already registered. Sign in with your password instead.",
        )
    recruiter = Recruiter(
        email=email,
        hashed_password=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        company_name=payload.company_name,
        phone=payload.phone,
    )
    db.add(recruiter)
    record_audit(
        db,
        actor_email=recruiter.email,
        actor_role="recruiter",
        action=AuditAction.REGISTER_RECRUITER,
        resource=str(recruiter.id),
        details=recruiter.company_name,
    )
    db.commit()
    db.refresh(recruiter)
    return recruiter


@router.post(
    "/admins/register",
    response_model=AdminOut,
    status_code=status.HTTP_201_CREATED,
)
def register_admin(payload: AdminRegister, db: Session = Depends(get_db)):
    email = normalize_email(str(payload.email))
    if _email_exists(email, db):
        raise HTTPException(
            status_code=409,
            detail="Email already registered. Sign in with your password instead.",
        )
    admin = Admin(
        email=email,
        hashed_password=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
    )
    db.add(admin)
    record_audit(
        db,
        actor_email=admin.email,
        actor_role="admin",
        action=AuditAction.REGISTER_ADMIN,
        resource=str(admin.id),
    )
    db.commit()
    db.refresh(admin)
    return admin


@router.post("/login", response_model=LoginResponse)
def login(
    response: Response,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    email = normalize_email(form.username)
    student = _find_student_by_email(db, email)
    if student and verify_password(form.password, student.hashed_password):
        role = "candidate" if form.client_id == "candidate" else "student"
        if form.client_id == "candidate" and student.account_kind != "candidate":
            student.account_kind = "candidate"
        record_audit(
            db,
            actor_email=student.email,
            actor_role=role,
            action=AuditAction.LOGIN,
        )
        result = _login_response(response, email=student.email, role=role, db=db)
        db.commit()
        return result

    recruiter = _find_recruiter_by_email(db, email)
    if recruiter and verify_password(form.password, recruiter.hashed_password):
        record_audit(
            db,
            actor_email=recruiter.email,
            actor_role="recruiter",
            action=AuditAction.LOGIN,
        )
        result = _login_response(
            response,
            email=recruiter.email,
            role="recruiter",
            db=db,
        )
        db.commit()
        return result

    admin = _find_admin_by_email(db, email)
    if admin and verify_password(form.password, admin.hashed_password):
        record_audit(
            db,
            actor_email=admin.email,
            actor_role="admin",
            action=AuditAction.LOGIN,
        )
        result = _login_response(response, email=admin.email, role="admin", db=db)
        db.commit()
        return result

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
    )


def _find_student_by_email(db: Session, email: str) -> Student | None:
    normalized = normalize_email(email)
    return db.query(Student).filter(func.lower(Student.email) == normalized).first()


def _find_recruiter_by_email(db: Session, email: str) -> Recruiter | None:
    normalized = normalize_email(email)
    return db.query(Recruiter).filter(func.lower(Recruiter.email) == normalized).first()


def _find_admin_by_email(db: Session, email: str) -> Admin | None:
    normalized = normalize_email(email)
    return db.query(Admin).filter(func.lower(Admin.email) == normalized).first()


def _email_exists(email: str, db: Session) -> bool:
    normalized = normalize_email(email)
    return bool(
        _find_student_by_email(db, normalized)
        or _find_recruiter_by_email(db, normalized)
        or _find_admin_by_email(db, normalized)
    )
