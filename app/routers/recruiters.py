from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.recruiter import Recruiter
from app.models.student import Student
from app.models.job import Job
from app.models.application import Application, ApplicationStatus
from app.models.recruiter_interview import RecruiterInterview
from app.schemas.recruiter import RecruiterRegister, RecruiterProfile
from app.schemas.student import StudentPublicProfile
from app.schemas.recruiter_tools import ATSRequest, InterviewCreate, InterviewUpdate
from app.auth import hash_password, verify_password, create_access_token, get_current_recruiter
from app.services.ats_simple import ats_score

router = APIRouter(prefix="/recruiters", tags=["recruiters"])


# ── AUTH ───────────────────────────────────────────────────────────────────────

@router.post("/register", response_model=RecruiterProfile, status_code=201)
def register(payload: RecruiterRegister, db: Session = Depends(get_db)):
    if db.query(Recruiter).filter(Recruiter.email == payload.email).first():
        raise HTTPException(409, "Email already registered")
    r = Recruiter(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
        company=getattr(payload, "company", None),
        job_title=getattr(payload, "job_title", None),
    )
    db.add(r); db.commit(); db.refresh(r)
    return r


@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    r = db.query(Recruiter).filter(Recruiter.email == email).first()
    if not r or not verify_password(password, r.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": create_access_token(r.email, "recruiter"), "token_type": "bearer", "role": "recruiter"}


# ── PROFILE ────────────────────────────────────────────────────────────────────

@router.get("/me", response_model=RecruiterProfile)
def get_profile(current: Recruiter = Depends(get_current_recruiter)):
    return current


@router.patch("/me", response_model=RecruiterProfile)
def update_profile(
    company:   str | None = None,
    job_title: str | None = None,
    first_name:str | None = None,
    last_name: str | None = None,
    current:   Recruiter  = Depends(get_current_recruiter),
    db:        Session    = Depends(get_db),
):
    if company:    current.company    = company
    if job_title:  current.job_title  = job_title
    if first_name: current.first_name = first_name
    if last_name:  current.last_name  = last_name
    db.commit(); db.refresh(current)
    return current


@router.delete("/me", status_code=204)
def delete_account(current: Recruiter = Depends(get_current_recruiter), db: Session = Depends(get_db)):
    db.delete(current); db.commit()


# ── STUDENTS ───────────────────────────────────────────────────────────────────

@router.get("/students", response_model=list[StudentPublicProfile])
def list_students(
    school:         str | None = Query(None),
    field_of_study: str | None = Query(None),
    skills:         str | None = Query(None),
    role:           str | None = Query(None),
    skip:           int        = Query(0,  ge=0),
    limit:          int        = Query(20, le=100),
    _:  Recruiter = Depends(get_current_recruiter),
    db: Session   = Depends(get_db),
):
    q = db.query(Student).filter(Student.is_visible == True)
    if school:         q = q.filter(Student.school.ilike(f"%{school}%"))
    if field_of_study: q = q.filter(Student.field_of_study.ilike(f"%{field_of_study}%"))
    if skills:         q = q.filter(Student.skills.ilike(f"%{skills}%"))
    if role:           q = q.filter(Student.role == role)
    return q.offset(skip).limit(limit).all()


@router.get("/students/{student_id}", response_model=StudentPublicProfile)
def get_student(
    student_id: str,
    _:  Recruiter = Depends(get_current_recruiter),
    db: Session   = Depends(get_db),
):
    s = db.query(Student).filter(Student.id == student_id, Student.is_visible == True).first()
    if not s: raise HTTPException(404, "Student not found")
    return s


# ── JOBS ───────────────────────────────────────────────────────────────────────

@router.post("/jobs", status_code=201)
def create_job(
    title:        str,
    description:  str,
    requirements: str | None = None,
    location:     str | None = None,
    current: Recruiter = Depends(get_current_recruiter),
    db:      Session   = Depends(get_db),
):
    job = Job(recruiter_id=current.id, title=title, description=description,
              requirements=requirements, location=location)
    db.add(job); db.commit(); db.refresh(job)
    return {"id": job.id, "title": job.title, "status": job.status, "is_active": job.is_active}


@router.get("/jobs")
def my_jobs(
    status:   str | None = Query(None),
    is_active:bool | None = Query(None),
    current: Recruiter = Depends(get_current_recruiter),
    db:      Session   = Depends(get_db),
):
    q = db.query(Job).filter(Job.recruiter_id == current.id)
    if status:            q = q.filter(Job.status == status)
    if is_active is not None: q = q.filter(Job.is_active == is_active)
    return [{"id": j.id, "title": j.title, "status": j.status,
             "is_active": j.is_active, "created_at": str(j.created_at)} for j in q.all()]


@router.get("/jobs/{job_id}")
def get_job(
    job_id:  int,
    current: Recruiter = Depends(get_current_recruiter),
    db:      Session   = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current.id).first()
    if not job: raise HTTPException(404, "Job not found")
    return {"id": job.id, "title": job.title, "description": job.description,
            "requirements": job.requirements, "location": job.location,
            "status": job.status, "is_active": job.is_active}


@router.patch("/jobs/{job_id}")
def update_job(
    job_id:       int,
    title:        str | None  = None,
    description:  str | None  = None,
    requirements: str | None  = None,
    location:     str | None  = None,
    is_active:    bool | None = None,
    status:       str | None  = None,
    current: Recruiter = Depends(get_current_recruiter),
    db:      Session   = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current.id).first()
    if not job: raise HTTPException(404, "Not found")
    if title:        job.title        = title
    if description:  job.description  = description
    if requirements: job.requirements = requirements
    if location:     job.location     = location
    if status:       job.status       = status
    if is_active is not None: job.is_active = is_active
    db.commit(); db.refresh(job)
    return {"id": job.id, "title": job.title, "is_active": job.is_active, "status": job.status}


@router.delete("/jobs/{job_id}", status_code=204)
def delete_job(
    job_id:  int,
    current: Recruiter = Depends(get_current_recruiter),
    db:      Session   = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current.id).first()
    if not job: raise HTTPException(404, "Not found")
    db.delete(job); db.commit()


# ── APPLICATIONS ───────────────────────────────────────────────────────────────

@router.get("/jobs/{job_id}/applications")
def job_applications(
    job_id:  int,
    status:  str | None = Query(None),
    current: Recruiter  = Depends(get_current_recruiter),
    db:      Session    = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current.id).first()
    if not job: raise HTTPException(403, "Not your job")
    q = db.query(Application).filter(Application.job_id == job_id)
    if status: q = q.filter(Application.status == status)
    return [{"id": a.id, "student_id": str(a.student_id), "status": a.status,
             "ats_score": a.ats_score, "cover_letter": a.cover_letter,
             "applied_at": str(a.applied_at)} for a in q.all()]


@router.patch("/applications/{app_id}/status")
def update_status(
    app_id:  int,
    status:  ApplicationStatus,
    current: Recruiter = Depends(get_current_recruiter),
    db:      Session   = Depends(get_db),
):
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app: raise HTTPException(404, "Not found")
    job = db.query(Job).filter(Job.id == app.job_id, Job.recruiter_id == current.id).first()
    if not job: raise HTTPException(403, "Not authorized")
    app.status = status; db.commit()
    return {"id": app_id, "status": app.status}


# ── ATS ────────────────────────────────────────────────────────────────────────

@router.post("/ats/score")
def score_cv(
    payload: ATSRequest,
    current: Recruiter = Depends(get_current_recruiter),
    db:      Session   = Depends(get_db),
):
    s = db.query(Student).filter(Student.id == payload.student_id).first()
    if not s: raise HTTPException(404, "Student not found")
    cv  = f"{s.skills or ''} {s.bio or ''} {s.field_of_study or ''}"
    res = ats_score(cv, payload.job_description, payload.requirements or "")
    return {"student_id": str(s.id), "full_name": f"{s.first_name} {s.last_name}",
            "cv_url": s.cv_url, **res}


@router.post("/ats/rank")
def rank_cvs(
    payload: ATSRequest,
    top_k:   int       = Query(10, ge=1, le=50),
    current: Recruiter = Depends(get_current_recruiter),
    db:      Session   = Depends(get_db),
):
    students = db.query(Student).filter(Student.is_visible == True).all()
    results  = sorted([
        {"student_id": str(s.id), "full_name": f"{s.first_name} {s.last_name}",
         "cv_url": s.cv_url,
         **ats_score(f"{s.skills or ''} {s.bio or ''} {s.field_of_study or ''}",
                     payload.job_description, payload.requirements or "")}
        for s in students
    ], key=lambda x: x["score"], reverse=True)
    return results[:top_k]


# ── INTERVIEWS ─────────────────────────────────────────────────────────────────

@router.post("/interviews", status_code=201)
def schedule(
    payload: InterviewCreate,
    current: Recruiter = Depends(get_current_recruiter),
    db:      Session   = Depends(get_db),
):
    i = RecruiterInterview(recruiter_id=current.id, **payload.model_dump())
    db.add(i); db.commit(); db.refresh(i)
    return {"id": i.id, "student_id": str(i.student_id),
            "scheduled_at": str(i.scheduled_at), "status": i.status}


@router.get("/interviews")
def list_interviews(
    status:  str | None = Query(None),
    current: Recruiter  = Depends(get_current_recruiter),
    db:      Session    = Depends(get_db),
):
    q = db.query(RecruiterInterview).filter(RecruiterInterview.recruiter_id == current.id)
    if status: q = q.filter(RecruiterInterview.status == status)
    return [{"id": i.id, "student_id": str(i.student_id), "job_title": i.job_title,
             "scheduled_at": str(i.scheduled_at), "status": i.status, "meeting_link": i.meeting_link}
            for i in q.order_by(RecruiterInterview.scheduled_at).all()]


@router.get("/interviews/{iid}")
def get_interview(
    iid:     int,
    current: Recruiter = Depends(get_current_recruiter),
    db:      Session   = Depends(get_db),
):
    i = db.query(RecruiterInterview).filter(
        RecruiterInterview.id == iid,
        RecruiterInterview.recruiter_id == current.id).first()
    if not i: raise HTTPException(404, "Not found")
    return {"id": i.id, "student_id": str(i.student_id), "job_title": i.job_title,
            "scheduled_at": str(i.scheduled_at), "duration_min": i.duration_min,
            "meeting_link": i.meeting_link, "notes": i.notes, "status": i.status}


@router.patch("/interviews/{iid}")
def update_interview(
    iid:     int,
    payload: InterviewUpdate,
    current: Recruiter = Depends(get_current_recruiter),
    db:      Session   = Depends(get_db),
):
    i = db.query(RecruiterInterview).filter(
        RecruiterInterview.id == iid,
        RecruiterInterview.recruiter_id == current.id).first()
    if not i: raise HTTPException(404, "Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(i, k, v)
    db.commit(); db.refresh(i)
    return {"id": i.id, "status": i.status, "scheduled_at": str(i.scheduled_at)}


@router.delete("/interviews/{iid}", status_code=204)
def cancel_interview(
    iid:     int,
    current: Recruiter = Depends(get_current_recruiter),
    db:      Session   = Depends(get_db),
):
    i = db.query(RecruiterInterview).filter(
        RecruiterInterview.id == iid,
        RecruiterInterview.recruiter_id == current.id).first()
    if not i: raise HTTPException(404, "Not found")
    db.delete(i); db.commit()


# ── DASHBOARD ──────────────────────────────────────────────────────────────────

@router.get("/dashboard")
def dashboard(
    current: Recruiter = Depends(get_current_recruiter),
    db:      Session   = Depends(get_db),
):
    job_ids  = [j.id for j in db.query(Job).filter(Job.recruiter_id == current.id).all()]
    total    = db.query(Application).filter(Application.job_id.in_(job_ids)).count() if job_ids else 0
    pending  = db.query(Application).filter(Application.job_id.in_(job_ids),
               Application.status == ApplicationStatus.pending).count() if job_ids else 0
    accepted = db.query(Application).filter(Application.job_id.in_(job_ids),
               Application.status == ApplicationStatus.accepted).count() if job_ids else 0
    interviews = db.query(RecruiterInterview).filter(
               RecruiterInterview.recruiter_id == current.id).count()
    return {
        "total_jobs":          len(job_ids),
        "active_jobs":         sum(1 for j in db.query(Job).filter(Job.recruiter_id == current.id).all() if j.is_active),
        "total_applications":  total,
        "pending":             pending,
        "accepted":            accepted,
        "total_interviews":    interviews,
    }
