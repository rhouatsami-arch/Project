from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_student
from app.models.student import Student
import os, re

router = APIRouter(prefix="/cv", tags=["cv-management"])

def _extract_text(path: str, ext: str) -> str:
    try:
        if ext == "pdf":
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                return " ".join(p.extract_text() or "" for p in pdf.pages)
        elif ext in ("doc","docx"):
            from docx import Document
            return " ".join(p.text for p in Document(path).paragraphs)
    except Exception:
        pass
    return ""

def _parse_cv(text: str) -> dict:
    emails  = re.findall(r"[\w.+-]+@[\w-]+\.\w+", text)
    phones  = re.findall(r"[\+]?[\d\s\-\(\)]{9,15}", text)
    urls    = re.findall(r"https?://\S+", text)
    skills_kw = ["python","java","javascript","react","fastapi","sql","ml","ai",
                 "docker","git","node","typescript","mongodb","postgresql","aws","azure"]
    found_skills = [s for s in skills_kw if s in text.lower()]
    return {
        "emails":  emails[:3],
        "phones":  [p.strip() for p in phones[:3]],
        "urls":    urls[:5],
        "skills_detected": found_skills,
        "word_count": len(text.split()),
        "raw_text_preview": text[:500],
    }

@router.post("/upload")
async def upload_cv(
    cv:      UploadFile = File(...),
    current: Student    = Depends(get_current_student),
    db:      Session    = Depends(get_db),
):
    ext = cv.filename.rsplit(".", 1)[-1].lower()
    if ext not in {"pdf","doc","docx"}: raise HTTPException(400, "PDF/DOC/DOCX only")
    contents = await cv.read()
    if len(contents) > 5*1024*1024: raise HTTPException(400, "Max 5MB")
    os.makedirs("uploads/cvs", exist_ok=True)
    path = f"uploads/cvs/student_{current.id}.{ext}"
    with open(path,"wb") as f: f.write(contents)
    current.cv_url = path; db.commit()
    extracted = _parse_cv(_extract_text(path, ext))
    return {"message": "CV uploaded", "cv_url": path, "extracted": extracted}

@router.get("/extract")
def extract_cv(current: Student = Depends(get_current_student)):
    if not current.cv_url: raise HTTPException(404, "No CV uploaded")
    ext  = current.cv_url.rsplit(".",1)[-1].lower()
    text = _extract_text(current.cv_url, ext)
    return _parse_cv(text)

@router.delete("/delete", status_code=204)
def delete_cv(current: Student = Depends(get_current_student), db: Session = Depends(get_db)):
    if current.cv_url and os.path.exists(current.cv_url):
        os.remove(current.cv_url)
    current.cv_url = None; db.commit()
