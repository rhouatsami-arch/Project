from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.auth import get_current_recruiter
from app.database import get_db
from app.models.recruitment import Job, JobStatus, Recruiter
from app.schemas.recruitment import JobCreate, JobOut, JobUpdate

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=list[JobOut])
def list_jobs(
    search: str | None = Query(None),
    location: str | None = Query(None),
    skill: str | None = Query(None),
    employment_type: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Job).filter(Job.status == JobStatus.open)
    if search:
        query = query.filter(or_(Job.title.ilike(f"%{search}%"), Job.description.ilike(f"%{search}%")))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if skill:
        query = query.filter(Job.required_skills.ilike(f"%{skill}%"))
    if employment_type:
        query = query.filter(Job.employment_type == employment_type)
    return query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/recruiter/me", response_model=list[JobOut])
def my_jobs(current: Recruiter = Depends(get_current_recruiter), db: Session = Depends(get_db)):
    return db.query(Job).filter(Job.recruiter_id == current.id).order_by(Job.created_at.desc()).all()


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.status == JobStatus.open).first()
    if not job:
        raise HTTPException(status_code=404, detail="Open job not found")
    return job


@router.post("/", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate, current: Recruiter = Depends(get_current_recruiter), db: Session = Depends(get_db)):
    job = Job(recruiter_id=current.id, **payload.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.patch("/{job_id}", response_model=JobOut)
def update_job(
    job_id: int,
    payload: JobUpdate,
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(job, field, value)
    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, current: Recruiter = Depends(get_current_recruiter), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
