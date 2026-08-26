from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.recruitment import Student
from app.modules.cv.service import CvService
from app.modules.platform.audit import AuditAction, record_audit
from app.schemas.cv import CvExtractedTextOut, CvUploadOut


def build_cv_routes(
    router: APIRouter,
    get_current_user,
):
    """Attach CV upload / extraction / download / delete routes to a user router."""

    @router.post(
        "/me/cv", response_model=CvUploadOut, status_code=status.HTTP_201_CREATED
    )
    async def upload_cv(
        file: UploadFile = File(...),
        current: Student = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        contents = await file.read()
        try:
            result = CvService.upload(current, file.filename or "cv.txt", contents)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        db.commit()
        db.refresh(current)
        role = getattr(current, "account_kind", None) or "student"
        record_audit(
            db,
            actor_email=current.email,
            actor_role=role,
            action=AuditAction.UPLOAD_CV,
            resource=str(current.id),
            details=result.filename,
        )
        db.commit()
        preview = result.raw_text[:500]
        if len(result.raw_text) > 500:
            preview += "..."
        return CvUploadOut(
            cv_filename=result.filename,
            extracted_char_count=result.char_count,
            extracted_text_preview=preview,
            skills_detected=result.skills,
            profile=current,
        )

    @router.get("/me/cv/extracted", response_model=CvExtractedTextOut)
    def get_cv_extracted_text(current: Student = Depends(get_current_user)):
        if not current.cv_filename:
            raise HTTPException(status_code=404, detail="No CV uploaded")
        data = CvService.get_extracted(current)
        return CvExtractedTextOut(**data)

    @router.get("/me/cv/download")
    def download_cv(current: Student = Depends(get_current_user)):
        if not current.cv_path or not Path(current.cv_path).is_file():
            raise HTTPException(status_code=404, detail="CV file not found on disk")
        return FileResponse(
            path=current.cv_path,
            filename=current.cv_filename or "cv",
            media_type="application/octet-stream",
        )

    @router.delete("/me/cv", status_code=status.HTTP_204_NO_CONTENT)
    def delete_cv(
        current: Student = Depends(get_current_user),
        db: Session = Depends(get_db),
    ):
        if not current.cv_filename:
            raise HTTPException(status_code=404, detail="No CV to delete")
        CvService.delete(current)
        role = getattr(current, "account_kind", None) or "student"
        record_audit(
            db,
            actor_email=current.email,
            actor_role=role,
            action=AuditAction.DELETE_CV,
            resource=str(current.id),
        )
        db.commit()
