from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.candidate import Candidate
from app.schemas.experience import ExperienceCreate, ExperienceUpdate, ExperienceOut
from app.routers.candidates import get_current_candidate
from app.models.experience import Experience

router = APIRouter(prefix="/candidates/me/experiences", tags=["candidate-experiences"])


@router.post("/", response_model=ExperienceOut, status_code=201)
def add_experience(
    payload: ExperienceCreate,
    current: Candidate = Depends(get_current_candidate),
    db:      Session   = Depends(get_db),
):
    exp = Experience(student_id=current.id, **payload.model_dump())
    db.add(exp); db.commit(); db.refresh(exp)
    return exp


@router.get("/", response_model=list[ExperienceOut])
def list_experiences(
    current: Candidate = Depends(get_current_candidate),
    db:      Session   = Depends(get_db),
):
    return db.query(Experience).filter(
        Experience.student_id == current.id
    ).order_by(Experience.start_date.desc()).all()


@router.get("/{exp_id}", response_model=ExperienceOut)
def get_experience(
    exp_id:  int,
    current: Candidate = Depends(get_current_candidate),
    db:      Session   = Depends(get_db),
):
    exp = db.query(Experience).filter(
        Experience.id == exp_id,
        Experience.student_id == current.id).first()
    if not exp: raise HTTPException(404, "Not found")
    return exp


@router.patch("/{exp_id}", response_model=ExperienceOut)
def update_experience(
    exp_id:  int,
    payload: ExperienceUpdate,
    current: Candidate = Depends(get_current_candidate),
    db:      Session   = Depends(get_db),
):
    exp = db.query(Experience).filter(
        Experience.id == exp_id,
        Experience.student_id == current.id).first()
    if not exp: raise HTTPException(404, "Not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(exp, k, v)
    db.commit(); db.refresh(exp)
    return exp


@router.delete("/{exp_id}", status_code=204)
def delete_experience(
    exp_id:  int,
    current: Candidate = Depends(get_current_candidate),
    db:      Session   = Depends(get_db),
):
    exp = db.query(Experience).filter(
        Experience.id == exp_id,
        Experience.student_id == current.id).first()
    if not exp: raise HTTPException(404, "Not found")
    db.delete(exp); db.commit()


@router.get("/summary/skills")
def skills_summary(
    current: Candidate = Depends(get_current_candidate),
    db:      Session   = Depends(get_db),
):
    from collections import Counter
    exps = db.query(Experience).filter(Experience.student_id == current.id).all()
    all_skills = []
    for e in exps:
        if e.skills_used:
            all_skills.extend([s.strip() for s in e.skills_used.split(",")])
    return {
        "total_experiences": len(exps),
        "current_position":  next(({"title": e.title, "company": e.company} for e in exps if e.is_current), None),
        "skills_frequency":  dict(Counter(all_skills).most_common(20)),
        "experience_types":  {t: sum(1 for e in exps if e.type == t) for t in set(e.type for e in exps)},
    }
