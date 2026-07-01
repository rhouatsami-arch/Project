import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.cv import CV, CVStatus
from app.schemas.cv import CVOut, CVDetailOut
from app.services.cv_extraction import validate_cv_upload, process_cv, detect_real_filetype
from app.services.cv_storage import generate_storage_path, save_file, delete_file
from app.auth import get_current_student

router = APIRouter(prefix="/cv", tags=["cv-management"])


@router.post("/upload", response_model=CVDetailOut, status_code=201)
async def upload_cv(
    file:    UploadFile = File(...),
    current  = Depends(get_current_student),
    db:      Session    = Depends(get_db),
):
    """
    Upload, store, and extract text from a CV in a single call.
    Validates real file content (not just extension) before processing.
    """
    contents = await file.read()

    is_valid, error = validate_cv_upload(contents, file.filename)
    if not is_valid:
        raise HTTPException(400, error)

    ext = detect_real_filetype(contents)
    path = generate_storage_path(str(current.id), ext)
    save_file(contents, path)

    # Mark previous CVs as not current
    db.query(CV).filter(CV.student_id == current.id, CV.is_current == True).update({"is_current": False})

    cv = CV(
        student_id=current.id,
        filename=file.filename,
        file_path=path,
        file_size=len(contents),
        file_ext=ext,
        status=CVStatus.processing,
        is_current=True,
    )
    db.add(cv); db.commit(); db.refresh(cv)

    # Extract text synchronously (move to background task / Celery for scale)
    result = process_cv(path, ext)
    if result["success"]:
        cv.raw_text       = result["raw_text"]
        cv.extracted_data = json.dumps(result["extracted_data"])
        cv.status          = CVStatus.extracted
    else:
        cv.status = CVStatus.failed
    import datetime
    cv.processed_at = datetime.datetime.utcnow()
    db.commit(); db.refresh(cv)

    # Sync to student.cv_url for backward compatibility
    current.cv_url = path
    db.commit()

    extracted = json.loads(cv.extracted_data) if cv.extracted_data else None
    return CVDetailOut(
        id=cv.id, filename=cv.filename, file_size=cv.file_size, file_ext=cv.file_ext,
        status=cv.status, is_current=cv.is_current, uploaded_at=cv.uploaded_at,
        processed_at=cv.processed_at, extracted=extracted,
    )


@router.get("/me", response_model=CVOut)
def get_current_cv(
    current = Depends(get_current_student),
    db:      Session = Depends(get_db),
):
    cv = db.query(CV).filter(CV.student_id == current.id, CV.is_current == True).first()
    if not cv: raise HTTPException(404, "No CV uploaded")
    return cv


@router.get("/me/extracted", response_model=CVDetailOut)
def get_extracted_data(
    current = Depends(get_current_student),
    db:      Session = Depends(get_db),
):
    cv = db.query(CV).filter(CV.student_id == current.id, CV.is_current == True).first()
    if not cv: raise HTTPException(404, "No CV uploaded")
    extracted = json.loads(cv.extracted_data) if cv.extracted_data else None
    return CVDetailOut(
        id=cv.id, filename=cv.filename, file_size=cv.file_size, file_ext=cv.file_ext,
        status=cv.status, is_current=cv.is_current, uploaded_at=cv.uploaded_at,
        processed_at=cv.processed_at, extracted=extracted,
    )


@router.get("/me/download")
def download_cv(
    current = Depends(get_current_student),
    db:      Session = Depends(get_db),
):
    cv = db.query(CV).filter(CV.student_id == current.id, CV.is_current == True).first()
    if not cv: raise HTTPException(404, "No CV uploaded")
    return FileResponse(cv.file_path, filename=cv.filename)


@router.get("/me/history", response_model=list[CVOut])
def cv_history(
    current = Depends(get_current_student),
    db:      Session = Depends(get_db),
):
    return db.query(CV).filter(CV.student_id == current.id).order_by(CV.uploaded_at.desc()).all()


@router.delete("/me", status_code=204)
def delete_current_cv(
    current = Depends(get_current_student),
    db:      Session = Depends(get_db),
):
    cv = db.query(CV).filter(CV.student_id == current.id, CV.is_current == True).first()
    if not cv: raise HTTPException(404, "No CV uploaded")
    delete_file(cv.file_path)
    db.delete(cv); db.commit()
    current.cv_url = None
    db.commit()


@router.post("/me/reprocess", response_model=CVDetailOut)
def reprocess_cv(
    current = Depends(get_current_student),
    db:      Session = Depends(get_db),
):
    """Re-run extraction on the current CV — useful after improving the parser."""
    cv = db.query(CV).filter(CV.student_id == current.id, CV.is_current == True).first()
    if not cv: raise HTTPException(404, "No CV uploaded")

    result = process_cv(cv.file_path, cv.file_ext)
    if result["success"]:
        cv.raw_text       = result["raw_text"]
        cv.extracted_data = json.dumps(result["extracted_data"])
        cv.status          = CVStatus.extracted
    else:
        cv.status = CVStatus.failed
    import datetime
    cv.processed_at = datetime.datetime.utcnow()
    db.commit(); db.refresh(cv)

    extracted = json.loads(cv.extracted_data) if cv.extracted_data else None
    return CVDetailOut(
        id=cv.id, filename=cv.filename, file_size=cv.file_size, file_ext=cv.file_ext,
        status=cv.status, is_current=cv.is_current, uploaded_at=cv.uploaded_at,
        processed_at=cv.processed_at, extracted=extracted,
    )
