from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.job import Job, JobStatus
from app.auth import get_current_student
from app.models.student import Student

router = APIRouter(prefix="/matching", tags=["ai-matching"])

@router.get("/jobs")
def match_jobs(
    top_k:   int = Query(10, ge=1, le=50),
    current: Student  = Depends(get_current_student),
    db:      Session  = Depends(get_db),
):
    from app.services.matching import match_student_to_jobs
    profile = f"{current.skills or ''} {current.bio or ''} {current.field_of_study or ''}"
    jobs = db.query(Job).filter(Job.is_active==True, Job.status==JobStatus.open).all()
    job_dicts = [{"id":j.id,"title":j.title,"description":j.description or "",
                  "requirements":j.requirements or "","location":j.location,
                  "recruiter_id":str(j.recruiter_id)} for j in jobs]
    ranked = match_student_to_jobs(profile, job_dicts)[:top_k]
    return {"student_id": str(current.id), "profile_used": profile[:200], "matches": ranked}

@router.post("/custom")
def match_custom_profile(
    profile: str,
    top_k:   int = Query(10, ge=1, le=50),
    db:      Session = Depends(get_db),
):
    from app.services.matching import match_student_to_jobs
    jobs = db.query(Job).filter(Job.is_active==True, Job.status==JobStatus.open).all()
    job_dicts = [{"id":j.id,"title":j.title,"description":j.description or "",
                  "requirements":j.requirements or "","location":j.location} for j in jobs]
    return match_student_to_jobs(profile, job_dicts)[:top_k]
