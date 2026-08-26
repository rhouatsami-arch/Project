from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_recruiter
from app.database import get_db
from app.models.recruitment import Job, Recruiter
from app.modules.offers.service import OfferService
from app.modules.platform.audit import AuditAction, record_audit
from app.schemas.recruitment import JobCreate, JobOut, JobUpdate

router = APIRouter(prefix="/jobs", tags=["jobs", "offers"])


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
    return OfferService.list_open(
        db,
        search=search,
        location=location,
        skill=skill,
        employment_type=employment_type,
        skip=skip,
        limit=limit,
    )


@router.get("/recruiter/me", response_model=list[JobOut])
def my_jobs(
    current: Recruiter = Depends(get_current_recruiter), db: Session = Depends(get_db)
):
    return OfferService.list_for_recruiter(db, current.id)


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = OfferService.get_open(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Open job not found")
    return job


@router.post("/", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreate,
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    job = OfferService.create(db, current, payload.model_dump())
    record_audit(
        db,
        actor_email=current.email,
        actor_role="recruiter",
        action=AuditAction.CREATE_JOB,
        resource=str(job.id),
        details=job.title,
    )
    db.commit()
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
    updated = OfferService.update(db, job, payload.model_dump(exclude_unset=True))
    record_audit(
        db,
        actor_email=current.email,
        actor_role="recruiter",
        action=AuditAction.UPDATE_JOB,
        resource=str(job.id),
        details=updated.title,
    )
    db.commit()
    return updated


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(
    job_id: int,
    current: Recruiter = Depends(get_current_recruiter),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.recruiter_id == current.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    title = job.title
    OfferService.delete(db, job)
    record_audit(
        db,
        actor_email=current.email,
        actor_role="recruiter",
        action=AuditAction.DELETE_JOB,
        resource=str(job_id),
        details=title,
    )
    db.commit()
