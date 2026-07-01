from fastapi import APIRouter
from app.services.ats import calculate_ats_score

router = APIRouter(prefix="/ats", tags=["ats"])

@router.post("/score")
def ats_score(cv_text: str, job_description: str):
    return calculate_ats_score(cv_text, job_description)