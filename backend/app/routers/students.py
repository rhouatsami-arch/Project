from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import get_current_student
from app.database import get_db
from app.models.recruitment import Application, Job, JobStatus, SavedJob, Student
from app.schemas.recruitment import ApplicationCreate, ApplicationOut, JobOut, SavedJobOut, StudentOut, StudentUpdate
from app.services.recruitment import candidate_match_score, extract_skills, extract_text_from_upload, save_cv

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/me", response_model=StudentOut)
def get_profile(current: Student = Depends(get_current_student)):
    return current


@router.patch("/me", response_model=StudentOut)
def update_profile(payload: StudentUpdate, current: Student = Depends(get_current_student), db: Session = Depends(get_db)):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current, field, value)
    db.commit()
    db.refresh(current)
    return current


@router.post("/me/cv", response_model=StudentOut)
async def upload_cv(file: UploadFile = File(...), current: Student = Depends(get_current_student), db: Session = Depends(get_db)):
    contents = await file.read()
    try:
        path = save_cv(str(current.id), file.filename, contents)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    extracted_text = extract_text_from_upload(file.filename, contents)
    extracted_skills = extract_skills(extracted_text)
    existing_skills = {skill.strip() for skill in (current.technical_skills or current.skills or "").split(",") if skill.strip()}
    merged_skills = sorted(existing_skills | set(extracted_skills))

    current.cv_filename = file.filename
    current.cv_path = path
    if merged_skills:
        current.technical_skills = ", ".join(merged_skills)
        current.skills = current.technical_skills
    db.commit()
    db.refresh(current)
    return current


@router.post("/jobs/{job_id}/apply", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def apply_to_job(
    job_id: int,
    payload: ApplicationCreate,
    current: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id, Job.status == JobStatus.open).first()
    if not job:
        raise HTTPException(status_code=404, detail="Open job not found")

    application = Application(
        student_id=current.id,
        job_id=job.id,
        cover_letter=payload.cover_letter,
        match_score=candidate_match_score(current.technical_skills or current.skills, job.required_skills),
    )
    db.add(application)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="You already applied to this job")
    db.refresh(application)
    return application


@router.get("/me/applications", response_model=list[ApplicationOut])
def my_applications(current: Student = Depends(get_current_student), db: Session = Depends(get_db)):
    return db.query(Application).filter(Application.student_id == current.id).order_by(Application.created_at.desc()).all()


@router.post("/jobs/{job_id}/save", response_model=SavedJobOut, status_code=status.HTTP_201_CREATED)
def save_job(job_id: int, current: Student = Depends(get_current_student), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.status == JobStatus.open).first()
    if not job:
        raise HTTPException(status_code=404, detail="Open job not found")

    saved = SavedJob(student_id=current.id, job_id=job.id)
    db.add(saved)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Job already saved")
    db.refresh(saved)
    return saved


@router.delete("/jobs/{job_id}/save", status_code=status.HTTP_204_NO_CONTENT)
def unsave_job(job_id: int, current: Student = Depends(get_current_student), db: Session = Depends(get_db)):
    saved = db.query(SavedJob).filter(SavedJob.student_id == current.id, SavedJob.job_id == job_id).first()
    if not saved:
        raise HTTPException(status_code=404, detail="Saved job not found")
    db.delete(saved)
    db.commit()


@router.get("/me/saved-jobs", response_model=list[SavedJobOut])
def my_saved_jobs(current: Student = Depends(get_current_student), db: Session = Depends(get_db)):
    return db.query(SavedJob).filter(SavedJob.student_id == current.id).order_by(SavedJob.created_at.desc()).all()
