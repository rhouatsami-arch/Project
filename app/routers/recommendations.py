from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.job import Job, JobStatus
from app.models.application import Application
from app.auth import get_current_student
from app.models.student import Student

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/jobs")
def recommend_jobs(
    top_k:   int = Query(5, ge=1, le=20),
    current: Student  = Depends(get_current_student),
    db:      Session  = Depends(get_db),
):
    from app.services.recommendations import get_collaborative_recommendations
    from app.services.matching import match_student_to_jobs
    all_apps = [{"student_id": a.student_id, "job_id": a.job_id}
                for a in db.query(Application).all()]
    applied  = {a["job_id"] for a in all_apps if str(a["student_id"]) == str(current.id)}
    all_jobs = [{"id":j.id,"title":j.title,"description":j.description or "",
                 "requirements":j.requirements or "","location":j.location,
                 "recruiter_id":str(j.recruiter_id),
                 "type":j.type,"status":j.status,"is_active":j.is_active,
                 "created_at":j.created_at}
                for j in db.query(Job).filter(Job.is_active==True,Job.status==JobStatus.open).all()]
    recs = get_collaborative_recommendations(current.id, all_apps, all_jobs, applied, top_k)
    if not recs:
        profile = f"{current.skills or ''} {current.bio or ''}"
        not_applied = [j for j in all_jobs if j["id"] not in applied]
        ranked = match_student_to_jobs(profile, not_applied)
        recs   = [r["job"] for r in ranked[:top_k]]
    return {"student_id": str(current.id), "recommendations": recs, "count": len(recs)}
