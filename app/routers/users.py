from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.student   import Student
from app.models.recruiter import Recruiter
from app.models.candidate import Candidate
from app.models.admin     import Admin
from app.auth import get_current_admin, hash_password

router = APIRouter(prefix="/users", tags=["user-management"])


# ── STUDENTS ───────────────────────────────────────────────────────────────────

@router.get("/students")
def list_students(
    search: str | None = Query(None),
    skip:   int        = Query(0,  ge=0),
    limit:  int        = Query(20, le=100),
    current: Admin   = Depends(get_current_admin),
    db:      Session = Depends(get_db),
):
    q = db.query(Student)
    if search:
        q = q.filter(
            Student.email.ilike(f"%{search}%") |
            Student.first_name.ilike(f"%{search}%") |
            Student.last_name.ilike(f"%{search}%")
        )
    return [{"id": str(s.id), "email": s.email,
             "full_name": f"{s.first_name} {s.last_name}",
             "school": s.school, "role": s.role,
             "is_visible": s.is_visible, "created_at": str(s.created_at)}
            for s in q.offset(skip).limit(limit).all()]


@router.get("/students/{uid}")
def get_student(uid: str, current: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    s = db.query(Student).filter(Student.id == uid).first()
    if not s: raise HTTPException(404, "Student not found")
    return {"id": str(s.id), "email": s.email, "first_name": s.first_name,
            "last_name": s.last_name, "school": s.school, "skills": s.skills,
            "role": s.role, "is_visible": s.is_visible, "cv_url": s.cv_url,
            "created_at": str(s.created_at)}


@router.patch("/students/{uid}")
def update_student(
    uid:        str,
    is_visible: bool | None = None,
    role:       str  | None = None,
    school:     str  | None = None,
    current: Admin   = Depends(get_current_admin),
    db:      Session = Depends(get_db),
):
    s = db.query(Student).filter(Student.id == uid).first()
    if not s: raise HTTPException(404, "Not found")
    if is_visible is not None: s.is_visible = is_visible
    if role:   s.role   = role
    if school: s.school = school
    db.commit(); db.refresh(s)
    return {"id": str(s.id), "email": s.email, "is_visible": s.is_visible, "role": s.role}


@router.delete("/students/{uid}", status_code=204)
def delete_student(uid: str, current: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    s = db.query(Student).filter(Student.id == uid).first()
    if not s: raise HTTPException(404, "Not found")
    db.delete(s); db.commit()


# ── RECRUITERS ─────────────────────────────────────────────────────────────────

@router.get("/recruiters")
def list_recruiters(
    search: str | None = Query(None),
    skip:   int        = Query(0,  ge=0),
    limit:  int        = Query(20, le=100),
    current: Admin   = Depends(get_current_admin),
    db:      Session = Depends(get_db),
):
    q = db.query(Recruiter)
    if search:
        q = q.filter(
            Recruiter.email.ilike(f"%{search}%") |
            Recruiter.first_name.ilike(f"%{search}%") |
            Recruiter.company.ilike(f"%{search}%")
        )
    return [{"id": str(r.id), "email": r.email,
             "full_name": f"{r.first_name} {r.last_name}",
             "company": r.company, "job_title": r.job_title,
             "created_at": str(r.created_at)}
            for r in q.offset(skip).limit(limit).all()]


@router.get("/recruiters/{uid}")
def get_recruiter(uid: str, current: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    r = db.query(Recruiter).filter(Recruiter.id == uid).first()
    if not r: raise HTTPException(404, "Not found")
    return {"id": str(r.id), "email": r.email, "first_name": r.first_name,
            "last_name": r.last_name, "company": r.company,
            "job_title": r.job_title, "created_at": str(r.created_at)}


@router.patch("/recruiters/{uid}")
def update_recruiter(
    uid:       str,
    company:   str | None = None,
    job_title: str | None = None,
    current: Admin   = Depends(get_current_admin),
    db:      Session = Depends(get_db),
):
    r = db.query(Recruiter).filter(Recruiter.id == uid).first()
    if not r: raise HTTPException(404, "Not found")
    if company:   r.company   = company
    if job_title: r.job_title = job_title
    db.commit(); db.refresh(r)
    return {"id": str(r.id), "email": r.email, "company": r.company}


@router.delete("/recruiters/{uid}", status_code=204)
def delete_recruiter(uid: str, current: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    r = db.query(Recruiter).filter(Recruiter.id == uid).first()
    if not r: raise HTTPException(404, "Not found")
    db.delete(r); db.commit()


# ── CANDIDATES ─────────────────────────────────────────────────────────────────

@router.get("/candidates")
def list_candidates(
    search: str | None = Query(None),
    status: str | None = Query(None),
    skip:   int        = Query(0,  ge=0),
    limit:  int        = Query(20, le=100),
    current: Admin   = Depends(get_current_admin),
    db:      Session = Depends(get_db),
):
    q = db.query(Candidate)
    if search:
        q = q.filter(
            Candidate.email.ilike(f"%{search}%") |
            Candidate.first_name.ilike(f"%{search}%")
        )
    if status: q = q.filter(Candidate.status == status)
    return [{"id": str(c.id), "email": c.email,
             "full_name": f"{c.first_name} {c.last_name}",
             "status": c.status, "location": c.location,
             "created_at": str(c.created_at)}
            for c in q.offset(skip).limit(limit).all()]


@router.patch("/candidates/{uid}")
def update_candidate(
    uid:    str,
    status: str | None = None,
    current: Admin   = Depends(get_current_admin),
    db:      Session = Depends(get_db),
):
    c = db.query(Candidate).filter(Candidate.id == uid).first()
    if not c: raise HTTPException(404, "Not found")
    if status: c.status = status
    db.commit(); db.refresh(c)
    return {"id": str(c.id), "email": c.email, "status": c.status}


@router.delete("/candidates/{uid}", status_code=204)
def delete_candidate(uid: str, current: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    c = db.query(Candidate).filter(Candidate.id == uid).first()
    if not c: raise HTTPException(404, "Not found")
    db.delete(c); db.commit()


# ── RESET PASSWORD ─────────────────────────────────────────────────────────────

@router.patch("/students/{uid}/reset-password", status_code=200)
def reset_student_password(
    uid:          str,
    new_password: str,
    current: Admin   = Depends(get_current_admin),
    db:      Session = Depends(get_db),
):
    s = db.query(Student).filter(Student.id == uid).first()
    if not s: raise HTTPException(404, "Not found")
    s.hashed_password = hash_password(new_password)
    db.commit()
    return {"message": "Password reset OK"}


@router.patch("/recruiters/{uid}/reset-password", status_code=200)
def reset_recruiter_password(
    uid:          str,
    new_password: str,
    current: Admin   = Depends(get_current_admin),
    db:      Session = Depends(get_db),
):
    r = db.query(Recruiter).filter(Recruiter.id == uid).first()
    if not r: raise HTTPException(404, "Not found")
    r.hashed_password = hash_password(new_password)
    db.commit()
    return {"message": "Password reset OK"}


# ── GLOBAL STATS ───────────────────────────────────────────────────────────────

@router.get("/stats")
def user_stats(current: Admin = Depends(get_current_admin), db: Session = Depends(get_db)):
    return {
        "students":   db.query(Student).count(),
        "recruiters": db.query(Recruiter).count(),
        "candidates": db.query(Candidate).count(),
        "admins":     db.query(Admin).count(),
        "total":      db.query(Student).count() + db.query(Recruiter).count() + db.query(Candidate).count(),
    }
