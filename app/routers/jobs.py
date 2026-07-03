from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.job import Job, JobStatus, JobType
from app.models.application import Application
from app.schemas.job import JobCreate, JobUpdate, JobOut
from app.auth import get_current_recruiter, get_current_student
from typing import Optional

router = APIRouter(prefix="/jobs", tags=["jobs"])


# ── PUBLIC — browse open jobs ──────────────────────────────────────────────────

@router.get("/", response_model=list[JobOut])
def list_jobs(
    search:   str | None = Query(None),
    location: str | None = Query(None),
    type:     str | None = Query(None),
    skip:     int        = Query(0,  ge=0),
    limit:    int        = Query(20, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Job).filter(Job.is_active == True, Job.status == JobStatus.open)
    if search:   q = q.filter(Job.title.ilike(f"%{search}%") | Job.description.ilike(f"%{search}%"))
    if location: q = q.filter(Job.location.ilike(f"%{location}%"))
    if type:     q = q.filter(Job.type == type)
    return q.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job: raise HTTPException(404, "Job not found")
    return job


# ── RECRUITER — manage own jobs ────────────────────────────────────────────────

@router.post("/", response_model=JobOut, status_code=201)
def create_job(
    payload: JobCreate,
    current  = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    job = Job(**payload.model_dump(), recruiter_id=current.id)
    db.add(job); db.commit(); db.refresh(job)
    return job


@router.patch("/{job_id}", response_model=JobOut)
def update_job(
    job_id:  int,
    payload: JobUpdate,
    current  = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current.id).first()
    if not job: raise HTTPException(404, "Not found or not yours")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(job, k, v)
    db.commit(); db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=204)
def delete_job(
    job_id:  int,
    current  = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current.id).first()
    if not job: raise HTTPException(404, "Not found")
    db.delete(job); db.commit()


@router.patch("/{job_id}/close", response_model=JobOut)
def close_job(
    job_id:  int,
    current  = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current.id).first()
    if not job: raise HTTPException(404, "Not found")
    job.status = JobStatus.closed; job.is_active = False
    db.commit(); db.refresh(job)
    return job


@router.patch("/{job_id}/reopen", response_model=JobOut)
def reopen_job(
    job_id:  int,
    current  = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current.id).first()
    if not job: raise HTTPException(404, "Not found")
    job.status = JobStatus.open; job.is_active = True
    db.commit(); db.refresh(job)
    return job


# ── JOB STATS ─────────────────────────────────────────────────────────────────

@router.get("/{job_id}/stats")
def job_stats(
    job_id:  int,
    current  = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current.id).first()
    if not job: raise HTTPException(404, "Not found")
    apps = db.query(Application).filter(Application.job_id == job_id).all()
    return {
        "job_id":             job_id,
        "title":              job.title,
        "status":             job.status,
        "total_applications": len(apps),
        "pending":    sum(1 for a in apps if a.status == "pending"),
        "reviewed":   sum(1 for a in apps if a.status == "reviewed"),
        "shortlisted":sum(1 for a in apps if a.status == "shortlisted"),
        "accepted":   sum(1 for a in apps if a.status == "accepted"),
        "rejected":   sum(1 for a in apps if a.status == "rejected"),
        "avg_ats":    round(sum(a.ats_score for a in apps if a.ats_score) /
                      max(sum(1 for a in apps if a.ats_score), 1), 1),
    }


# ── SIMILAR JOBS (content-based) ──────────────────────────────────────────────

@router.get("/{job_id}/similar", response_model=list[JobOut])
def similar_jobs(
    job_id: int,
    top_k:  int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job: raise HTTPException(404, "Not found")
    others = db.query(Job).filter(
        Job.id != job_id,
        Job.is_active == True,
        Job.status == JobStatus.open
    ).all()
    if not others: return []
    try:
        from app.services.matching import match_student_to_jobs
        profile = f"{job.title} {job.description or ''} {job.requirements or ''}"
        ranked  = match_student_to_jobs(profile, [
            {"id": j.id, "title": j.title,
             "description": j.description or "",
             "requirements": j.requirements or "",
             "location": j.location}
            for j in others
        ])
        ids = [r["job"]["id"] for r in ranked[:top_k]]
        return [j for j in others if j.id in ids]
    except Exception:
        return others[:top_k]
