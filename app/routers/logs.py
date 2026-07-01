import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_admin
from app.models.student import Student
from app.models.recruiter import Recruiter
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.application import Application
from app.models.recruiter_interview import RecruiterInterview

router = APIRouter(prefix="/logs", tags=["tracking-logs"])

@router.get("/activity")
def activity_summary(
    days: int = Query(7, ge=1, le=90),
    current  = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    from datetime import timedelta
    since = datetime.datetime.utcnow() - timedelta(days=days)
    return {
        "period_days":          days,
        "new_students":         db.query(Student).filter(Student.created_at >= since).count(),
        "new_recruiters":       db.query(Recruiter).filter(Recruiter.created_at >= since).count(),
        "new_candidates":       db.query(Candidate).filter(Candidate.created_at >= since).count(),
        "new_jobs":             db.query(Job).filter(Job.created_at >= since).count(),
        "new_applications":     db.query(Application).filter(Application.applied_at >= since).count(),
        "new_interviews":       db.query(RecruiterInterview).filter(RecruiterInterview.created_at >= since).count(),
    }

@router.get("/platform")
def platform_overview(current = Depends(get_current_admin), db: Session = Depends(get_db)):
    total_apps  = db.query(Application).count()
    accepted    = db.query(Application).filter(Application.status == "accepted").count()
    rejected    = db.query(Application).filter(Application.status == "rejected").count()
    pending     = db.query(Application).filter(Application.status == "pending").count()
    active_jobs = db.query(Job).filter(Job.is_active == True).count()
    return {
        "users": {
            "students":   db.query(Student).count(),
            "recruiters": db.query(Recruiter).count(),
            "candidates": db.query(Candidate).count(),
        },
        "jobs": {
            "total":  db.query(Job).count(),
            "active": active_jobs,
            "closed": db.query(Job).filter(Job.is_active == False).count(),
        },
        "applications": {
            "total":    total_apps,
            "pending":  pending,
            "accepted": accepted,
            "rejected": rejected,
            "acceptance_rate": round(accepted / max(total_apps,1) * 100, 1),
        },
        "interviews": {
            "total":     db.query(RecruiterInterview).count(),
            "scheduled": db.query(RecruiterInterview).filter(RecruiterInterview.status=="scheduled").count(),
            "completed": db.query(RecruiterInterview).filter(RecruiterInterview.status=="completed").count(),
        },
    }

@router.get("/top-jobs")
def top_jobs(
    limit: int = Query(10, le=50),
    current = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    from sqlalchemy import func
    results = (db.query(Job.id, Job.title, func.count(Application.id).label("apps"))
               .join(Application, Application.job_id == Job.id, isouter=True)
               .group_by(Job.id).order_by(func.count(Application.id).desc())
               .limit(limit).all())
    return [{"job_id":r.id,"title":r.title,"total_applications":r.apps} for r in results]

@router.get("/top-recruiters")
def top_recruiters(
    limit: int = Query(10, le=50),
    current = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    from sqlalchemy import func
    results = (db.query(Job.recruiter_id, func.count(Job.id).label("jobs"))
               .group_by(Job.recruiter_id)
               .order_by(func.count(Job.id).desc())
               .limit(limit).all())
    return [{"recruiter_id": str(r.recruiter_id), "total_jobs": r.jobs} for r in results]
