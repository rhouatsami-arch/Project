from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.auth import get_current_student
from app.models.student import Student
from app.models.job import Job
from app.services.ats_simple import ats_score

router = APIRouter(prefix="/ai", tags=["ai-explanation"])

class ExplainRequest(BaseModel):
    job_id: int

@router.post("/explain-match")
def explain_match(
    payload: ExplainRequest,
    current: Student  = Depends(get_current_student),
    db:      Session  = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == payload.job_id).first()
    if not job: raise HTTPException(404, "Job not found")
    cv_text = f"{current.skills or ''} {current.bio or ''} {current.field_of_study or ''}"
    result  = ats_score(cv_text, job.description, job.requirements or "")
    strengths = result["matched_keywords"][:10]
    gaps      = result["missing_keywords"][:10]
    return {
        "job_id":    job.id,
        "job_title": job.title,
        "score":     result["score"],
        "semantic_score":  result["semantic_score"],
        "keyword_score":   result["keyword_score"],
        "explanation": {
            "strengths": f"Your profile matches on: {', '.join(strengths) if strengths else 'general skills'}",
            "gaps":      f"Missing keywords: {', '.join(gaps) if gaps else 'none detected'}",
            "verdict":   result["recommendation"],
            "advice":    f"Add these to your CV/profile to improve your score: {', '.join(gaps[:5])}" if gaps else "Your profile is well aligned.",
        }
    }

@router.post("/explain-ats")
def explain_ats(
    cv_text:         str,
    job_description: str,
    requirements:    str = "",
):
    result = ats_score(cv_text, job_description, requirements)
    return {
        **result,
        "explanation": {
            "how_score_works": "60% semantic similarity (sentence embeddings) + 40% keyword overlap",
            "matched":  result["matched_keywords"],
            "missing":  result["missing_keywords"],
            "advice":   f"Add these keywords: {', '.join(result['missing_keywords'][:5])}" if result["missing_keywords"] else "Good coverage.",
        }
    }
