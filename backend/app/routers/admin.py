from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_admin
from app.database import get_db
from app.models.platform import Admin, AuditLog, Meeting, RecommendationHistory
from app.models.recruitment import Application, Job, Recruiter, Student
from app.modules.platform.audit import AuditAction, audit_to_dict, record_audit
from app.modules.users.service import UserService
from app.schemas.platform import (
    AdminApplicantOut,
    AdminCreateCandidate,
    AdminCreateRecruiter,
    AdminCreateStudent,
    AdminDashboardOut,
    AdminOut,
    AdminRecruiterOut,
    AuditLogOut,
)

router = APIRouter(prefix="/admin", tags=["admin", "administration"])


def _email_taken(email: str, db: Session) -> bool:
    return bool(
        db.query(Student).filter(Student.email == email).first()
        or db.query(Recruiter).filter(Recruiter.email == email).first()
        or db.query(Admin).filter(Admin.email == email).first()
    )


def _applicant_out(student: Student) -> AdminApplicantOut:
    return AdminApplicantOut(
        id=student.id,
        email=student.email,
        first_name=student.first_name,
        last_name=student.last_name,
        university=student.university,
        field_of_study=student.field_of_study,
        account_kind=student.account_kind or "student",
        created_at=student.created_at.isoformat(),
    )


def _recruiter_out(recruiter: Recruiter) -> AdminRecruiterOut:
    return AdminRecruiterOut(
        id=recruiter.id,
        email=recruiter.email,
        first_name=recruiter.first_name,
        last_name=recruiter.last_name,
        company_name=recruiter.company_name,
        phone=recruiter.phone,
        created_at=recruiter.created_at.isoformat(),
    )


def _audit_log_out(log: AuditLog) -> AuditLogOut:
    return AuditLogOut(**audit_to_dict(log))


def _audit(
    db: Session,
    *,
    admin: Admin,
    action: str,
    resource: str,
    details: str | None = None,
) -> None:
    record_audit(
        db,
        actor_email=admin.email,
        actor_role="admin",
        action=action,
        resource=resource,
        details=details,
    )


@router.get("/me", response_model=AdminOut)
def get_profile(current: Admin = Depends(get_current_admin)):
    return current


@router.get("/dashboard", response_model=AdminDashboardOut)
def dashboard(
    current: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(10).all()
    return AdminDashboardOut(
        total_students=db.query(Student)
        .filter(Student.account_kind == "student")
        .count(),
        total_candidates=db.query(Student)
        .filter(Student.account_kind == "candidate")
        .count(),
        total_recruiters=db.query(Recruiter).count(),
        total_jobs=db.query(Job).count(),
        total_applications=db.query(Application).count(),
        total_meetings=db.query(Meeting).count(),
        total_recommendations=db.query(RecommendationHistory).count(),
        recent_audit_logs=[_audit_log_out(log) for log in logs],
    )


@router.get("/users/students", response_model=list[AdminApplicantOut])
def list_students(
    current: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
):
    students = (
        db.query(Student)
        .filter(Student.account_kind == "student")
        .order_by(Student.created_at.desc())
        .limit(200)
        .all()
    )
    return [_applicant_out(item) for item in students]


@router.get("/users/candidates", response_model=list[AdminApplicantOut])
def list_candidates(
    current: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
):
    candidates = (
        db.query(Student)
        .filter(Student.account_kind == "candidate")
        .order_by(Student.created_at.desc())
        .limit(200)
        .all()
    )
    return [_applicant_out(item) for item in candidates]


@router.get("/users/recruiters", response_model=list[AdminRecruiterOut])
def list_recruiters(
    current: Admin = Depends(get_current_admin), db: Session = Depends(get_db)
):
    recruiters = (
        db.query(Recruiter).order_by(Recruiter.created_at.desc()).limit(200).all()
    )
    return [_recruiter_out(item) for item in recruiters]


@router.post(
    "/users/students",
    response_model=AdminApplicantOut,
    status_code=status.HTTP_201_CREATED,
)
def create_student(
    payload: AdminCreateStudent,
    current: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if _email_taken(payload.email, db):
        raise HTTPException(status_code=409, detail="Email already registered")
    student = UserService.create_student(
        db, payload.model_dump(), account_kind="student"
    )
    _audit(
        db,
        admin=current,
        action=AuditAction.CREATE_STUDENT,
        resource=str(student.id),
        details=student.email,
    )
    db.commit()
    return _applicant_out(student)


@router.post(
    "/users/candidates",
    response_model=AdminApplicantOut,
    status_code=status.HTTP_201_CREATED,
)
def create_candidate(
    payload: AdminCreateCandidate,
    current: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if _email_taken(payload.email, db):
        raise HTTPException(status_code=409, detail="Email already registered")
    data = payload.model_dump()
    data["internship_type"] = None
    data["internship_duration"] = None
    candidate = UserService.create_student(db, data, account_kind="candidate")
    _audit(
        db,
        admin=current,
        action=AuditAction.CREATE_CANDIDATE,
        resource=str(candidate.id),
        details=candidate.email,
    )
    db.commit()
    return _applicant_out(candidate)


@router.post(
    "/users/recruiters",
    response_model=AdminRecruiterOut,
    status_code=status.HTTP_201_CREATED,
)
def create_recruiter(
    payload: AdminCreateRecruiter,
    current: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if _email_taken(payload.email, db):
        raise HTTPException(status_code=409, detail="Email already registered")
    recruiter = UserService.create_recruiter(db, payload.model_dump())
    _audit(
        db,
        admin=current,
        action=AuditAction.CREATE_RECRUITER,
        resource=str(recruiter.id),
        details=recruiter.email,
    )
    db.commit()
    return _recruiter_out(recruiter)


@router.delete("/users/students/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    user_id: UUID,
    current: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    student = (
        db.query(Student)
        .filter(Student.id == user_id, Student.account_kind == "student")
        .first()
    )
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    email = student.email
    UserService.delete_student(student, db)
    _audit(
        db,
        admin=current,
        action=AuditAction.DELETE_STUDENT,
        resource=str(user_id),
        details=email,
    )
    db.commit()


@router.delete("/users/candidates/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_candidate(
    user_id: UUID,
    current: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    candidate = (
        db.query(Student)
        .filter(Student.id == user_id, Student.account_kind == "candidate")
        .first()
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    email = candidate.email
    UserService.delete_student(candidate, db)
    _audit(
        db,
        admin=current,
        action=AuditAction.DELETE_CANDIDATE,
        resource=str(user_id),
        details=email,
    )
    db.commit()


@router.delete("/users/recruiters/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recruiter(
    user_id: UUID,
    current: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    recruiter = db.query(Recruiter).filter(Recruiter.id == user_id).first()
    if not recruiter:
        raise HTTPException(status_code=404, detail="Recruiter not found")
    email = recruiter.email
    UserService.delete_recruiter(recruiter, db)
    _audit(
        db,
        admin=current,
        action=AuditAction.DELETE_RECRUITER,
        resource=str(user_id),
        details=email,
    )
    db.commit()


@router.get("/audit-logs", response_model=list[AuditLogOut])
def audit_logs(
    current: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
    role: str | None = None,
    action: str | None = None,
    limit: int = 100,
):
    query = db.query(AuditLog).order_by(AuditLog.created_at.desc())
    if role:
        query = query.filter(AuditLog.actor_role == role)
    if action:
        query = query.filter(AuditLog.action == action)
    logs = query.limit(min(limit, 200)).all()
    return [_audit_log_out(log) for log in logs]
