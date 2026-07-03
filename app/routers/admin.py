from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.admin import Admin
from app.models.student import Student
from app.models.recruiter import Recruiter
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.application import Application
from app.models.recruiter_interview import RecruiterInterview
from app.models.quiz import Quiz
from app.schemas.admin import AdminRegister, AdminOut, AdminStats
from app.auth import hash_password, get_current_admin, create_access_token, verify_password

router = APIRouter(prefix="/admin", tags=["admin"])


# ── AUTH ───────────────────────────────────────────────────────────────────────

@router.post("/register", response_model=AdminOut, status_code=201)
def register_admin(payload: AdminRegister, db: Session = Depends(get_db)):
    if db.query(Admin).filter(Admin.email == payload.email).first():
        raise HTTPException(409, "Email already registered")
    a = Admin(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
    )
    db.add(a); db.commit(); db.refresh(a)
    return a


@router.post("/login")
def login_admin(email: str, password: str, db: Session = Depends(get_db)):
    a = db.query(Admin).filter(Admin.email == email, Admin.is_active == True).first()
    if not a or not verify_password(password, a.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": create_access_token(a.email, "admin"), "token_type": "bearer"}


# ── DASHBOARD STATS ────────────────────────────────────────────────────────────

@router.get("/dashboard", response_model=AdminStats)
def dashboard(current: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    return AdminStats(
        total_students=    db.query(Student).count(),
        total_recruiters=  db.query(Recruiter).count(),
        total_candidates=  db.query(Candidate).count(),
        total_jobs=        db.query(Job).count(),
        total_applications=db.query(Application).count(),
        total_interviews=  db.query(RecruiterInterview).count(),
        total_quizzes=     db.query(Quiz).count(),
    )


# ── USERS MANAGEMENT ───────────────────────────────────────────────────────────

@router.get("/users/students", response_model=list)
def list_students(
    skip:  int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    current: Admin   = Depends(get_current_admin),
    db:      Session = Depends(get_db),
):
    return [{"id": str(s.id), "email": s.email, "full_name": f"{s.first_name} {s.last_name}",
             "school": s.school, "is_visible": s.is_visible, "created_at": str(s.created_at)}
            for s in db.query(Student).offset(skip).limit(limit).all()]


@router.get("/users/recruiters", response_model=list)
def list_recruiters(
    skip:  int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    current: Admin   = Depends(get_current_admin),
    db:      Session = Depends(get_db),
):
    return [{"id": str(r.id), "email": r.email, "full_name": f"{r.first_name} {r.last_name}",
             "company": r.company, "created_at": str(r.created_at)}
            for r in db.query(Recruiter).offset(skip).limit(limit).all()]


@router.get("/users/candidates", response_model=list)
def list_candidates(
    skip:  int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    current: Admin   = Depends(get_current_admin),
    db:      Session = Depends(get_db),
):
    return [{"id": str(c.id), "email": c.email, "full_name": f"{c.first_name} {c.last_name}",
             "status": c.status, "created_at": str(c.created_at)}
            for c in db.query(Candidate).offset(skip).limit(limit).all()]


@router.delete("/users/students/{student_id}", status_code=204)
def delete_student(
    student_id: str,
    current: Admin   = Depends(get_current_admin),
    db:      Session = Depends(get_db),
):
    s = db.query(Student).filter(Student.id == student_id).first()
    if not s: raise HTTPException(404, "Not found")
    db.delete(s); db.commit()


@router.delete("/users/recruiters/{recruiter_id}", status_code=204)
def delete_recruiter(
    recruiter_id: str,
    current: Admin   = Depends(get_current_admin),
    db:      Session = Depends(get_db),
):
    r = db.query(Recruiter).filter(Recruiter.id == recruiter_id).first()
    if not r: raise HTTPException(404, "Not found")
    db.delete(r); db.commit()


@router.delete("/users/candidates/{candidate_id}", status_code=204)
def delete_candidate(
    candidate_id: str,
    current: Admin   = Depends(get_current_admin),
    db:      Session = Depends(get_db),
):
    c = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not c: raise HTTPException(404, "Not found")
    db.delete(c); db.commit()


# ── JOBS CONTROL ───────────────────────────────────────────────────────────────

@router.get("/jobs")
def list_all_jobs(
    skip:  int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    current: Admin   = Depends(get_current_admin),
    db:      Session = Depends(get_db),
):
    return [{"id": j.id, "title": j.title, "recruiter_id": str(j.recruiter_id),
             "status": j.status, "is_active": j.is_active, "created_at": str(j.created_at)}
            for j in db.query(Job).offset(skip).limit(limit).all()]


@router.patch("/jobs/{job_id}/toggle")
def toggle_job(
    job_id:  int,
    current: Admin   = Depends(get_current_admin),
    db:      Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job: raise HTTPException(404, "Not found")
    job.is_active = not job.is_active
    db.commit()
    return {"id": job_id, "is_active": job.is_active}


@router.delete("/jobs/{job_id}", status_code=204)
def delete_job(
    job_id:  int,
    current: Admin   = Depends(get_current_admin),
    db:      Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job: raise HTTPException(404, "Not found")
    db.delete(job); db.commit()


# ── APPLICATIONS CONTROL ───────────────────────────────────────────────────────

@router.get("/applications")
def list_all_applications(
    skip:  int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    current: Admin   = Depends(get_current_admin),
    db:      Session = Depends(get_db),
):
    return [{"id": a.id, "student_id": str(a.student_id), "job_id": a.job_id,
             "status": a.status, "ats_score": a.ats_score, "applied_at": str(a.applied_at)}
            for a in db.query(Application).offset(skip).limit(limit).all()]


# ── ADMINS MANAGEMENT ──────────────────────────────────────────────────────────

@router.get("/admins", response_model=list[AdminOut])
def list_admins(current: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    if not current.is_superadmin:
        raise HTTPException(403, "Superadmin only")
    return db.query(Admin).all()


@router.patch("/admins/{admin_id}/toggle")
def toggle_admin(
    admin_id: str,
    current:  Admin   = Depends(get_current_admin),
    db:       Session = Depends(get_db),
):
    if not current.is_superadmin:
        raise HTTPException(403, "Superadmin only")
    a = db.query(Admin).filter(Admin.id == admin_id).first()
    if not a: raise HTTPException(404, "Not found")
    a.is_active = not a.is_active
    db.commit()
    return {"id": admin_id, "is_active": a.is_active}


# ── SYSTEM LOGS (simple) ───────────────────────────────────────────────────────

@router.get("/logs/summary")
def logs_summary(current: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    week_ago = datetime.utcnow() - timedelta(days=7)
    return {
        "new_students_last_7d":   db.query(Student).filter(Student.created_at >= week_ago).count(),
        "new_jobs_last_7d":       db.query(Job).filter(Job.created_at >= week_ago).count(),
        "new_applications_last_7d": db.query(Application).filter(Application.applied_at >= week_ago).count(),
        "active_jobs":            db.query(Job).filter(Job.is_active == True).count(),
        "inactive_jobs":          db.query(Job).filter(Job.is_active == False).count(),
    }
