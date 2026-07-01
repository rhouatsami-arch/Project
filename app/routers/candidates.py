from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
import os
from app.database import get_db
from app.models.candidate import Candidate, CandidateDocument, CandidateApplication, CandidateFavorite, AppStatus
from app.schemas.candidate import (
    CandidateRegister, CandidateUpdate, CandidateProfile,
    ApplicationCreate, ApplicationOut, FavoriteOut, DocumentOut, CandidateStats
)
from app.auth import hash_password, verify_password, create_access_token, _decode_token
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
router = APIRouter(prefix="/candidates", tags=["candidates"])


def get_current_candidate(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Candidate:
    payload = _decode_token(token)
    if payload.get("role") != "candidate":
        raise HTTPException(403, "Not a candidate account")
    if not (c := db.query(Candidate).filter(Candidate.email == payload["sub"]).first()):
        raise HTTPException(401, "Candidate not found")
    return c


# ── AUTH ───────────────────────────────────────────────────────────────────────

@router.post("/register", response_model=CandidateProfile, status_code=201)
def register(payload: CandidateRegister, db: Session = Depends(get_db)):
    if db.query(Candidate).filter(Candidate.email == payload.email).first():
        raise HTTPException(409, "Email already registered")
    c = Candidate(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
    )
    db.add(c); db.commit(); db.refresh(c)
    return c


@router.post("/login")
def login(payload: CandidateRegister, db: Session = Depends(get_db)):
    c = db.query(Candidate).filter(Candidate.email == payload.email).first()
    if not c or not verify_password(payload.password, c.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    return {"access_token": create_access_token(c.email, "candidate"), "token_type": "bearer", "role": "candidate"}


# ── PROFILE ────────────────────────────────────────────────────────────────────

@router.get("/me", response_model=CandidateProfile)
def get_profile(current: Candidate = Depends(get_current_candidate)):
    return current


@router.patch("/me", response_model=CandidateProfile)
def update_profile(
    payload: CandidateUpdate,
    current: Candidate = Depends(get_current_candidate),
    db:      Session   = Depends(get_db),
):
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(current, k, v)
    db.commit(); db.refresh(current)
    return current


@router.delete("/me", status_code=204)
def delete_account(current: Candidate = Depends(get_current_candidate), db: Session = Depends(get_db)):
    db.delete(current); db.commit()


# ── CV ─────────────────────────────────────────────────────────────────────────

@router.post("/me/cv")
async def upload_cv(
    cv:      UploadFile = File(...),
    current: Candidate  = Depends(get_current_candidate),
    db:      Session    = Depends(get_db),
):
    if cv.filename.rsplit(".", 1)[-1].lower() != "pdf":
        raise HTTPException(400, "Only PDF allowed")
    contents = await cv.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(400, "Max 5MB")
    os.makedirs("uploads/candidates/cvs", exist_ok=True)
    path = f"uploads/candidates/cvs/candidate_{current.id}.pdf"
    with open(path, "wb") as f: f.write(contents)
    current.cv_url = path; db.commit()
    return {"message": "CV uploaded", "cv_url": path}


@router.get("/me/cv")
def get_cv(current: Candidate = Depends(get_current_candidate)):
    if not current.cv_url: raise HTTPException(404, "No CV uploaded")
    return {"cv_url": current.cv_url}


@router.delete("/me/cv", status_code=204)
def delete_cv(current: Candidate = Depends(get_current_candidate), db: Session = Depends(get_db)):
    current.cv_url = None; db.commit()


# ── DOCUMENTS ──────────────────────────────────────────────────────────────────

@router.post("/me/documents", response_model=DocumentOut, status_code=201)
async def add_document(
    name:     str        = "document",
    doc_type: str        = "other",
    file:     UploadFile = File(...),
    current:  Candidate  = Depends(get_current_candidate),
    db:       Session    = Depends(get_db),
):
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024: raise HTTPException(400, "Max 10MB")
    os.makedirs("uploads/candidates/docs", exist_ok=True)
    path = f"uploads/candidates/docs/candidate_{current.id}_{file.filename}"
    with open(path, "wb") as f: f.write(contents)
    doc = CandidateDocument(candidate_id=current.id, name=name, type=doc_type, file_url=path)
    db.add(doc); db.commit(); db.refresh(doc)
    return doc


@router.get("/me/documents", response_model=list[DocumentOut])
def list_documents(current: Candidate = Depends(get_current_candidate), db: Session = Depends(get_db)):
    return db.query(CandidateDocument).filter(CandidateDocument.candidate_id == current.id).all()


@router.delete("/me/documents/{doc_id}", status_code=204)
def delete_document(
    doc_id:  int,
    current: Candidate = Depends(get_current_candidate),
    db:      Session   = Depends(get_db),
):
    doc = db.query(CandidateDocument).filter(
        CandidateDocument.id == doc_id,
        CandidateDocument.candidate_id == current.id).first()
    if not doc: raise HTTPException(404, "Not found")
    db.delete(doc); db.commit()


# ── APPLICATIONS ───────────────────────────────────────────────────────────────

@router.get("/me/applications", response_model=list[ApplicationOut])
def list_applications(current: Candidate = Depends(get_current_candidate), db: Session = Depends(get_db)):
    return db.query(CandidateApplication).filter(CandidateApplication.candidate_id == current.id).all()


@router.post("/me/applications", response_model=ApplicationOut, status_code=201)
def apply(
    payload: ApplicationCreate,
    current: Candidate = Depends(get_current_candidate),
    db:      Session   = Depends(get_db),
):
    if db.query(CandidateApplication).filter_by(candidate_id=current.id, job_id=payload.job_id).first():
        raise HTTPException(409, "Already applied")
    app = CandidateApplication(candidate_id=current.id, **payload.model_dump())
    db.add(app); db.commit(); db.refresh(app)
    return app


@router.get("/me/applications/{app_id}", response_model=ApplicationOut)
def get_application(
    app_id:  int,
    current: Candidate = Depends(get_current_candidate),
    db:      Session   = Depends(get_db),
):
    app = db.query(CandidateApplication).filter(
        CandidateApplication.id == app_id,
        CandidateApplication.candidate_id == current.id).first()
    if not app: raise HTTPException(404, "Not found")
    return app


@router.delete("/me/applications/{app_id}", status_code=204)
def cancel_application(
    app_id:  int,
    current: Candidate = Depends(get_current_candidate),
    db:      Session   = Depends(get_db),
):
    app = db.query(CandidateApplication).filter(
        CandidateApplication.id == app_id,
        CandidateApplication.candidate_id == current.id).first()
    if not app: raise HTTPException(404, "Not found")
    db.delete(app); db.commit()


# ── FAVORITES ──────────────────────────────────────────────────────────────────

@router.get("/me/favorites", response_model=list[FavoriteOut])
def list_favorites(current: Candidate = Depends(get_current_candidate), db: Session = Depends(get_db)):
    return db.query(CandidateFavorite).filter(CandidateFavorite.candidate_id == current.id).all()


@router.post("/me/favorites/{job_id}", response_model=FavoriteOut, status_code=201)
def add_favorite(
    job_id:  int,
    current: Candidate = Depends(get_current_candidate),
    db:      Session   = Depends(get_db),
):
    if db.query(CandidateFavorite).filter_by(candidate_id=current.id, job_id=job_id).first():
        raise HTTPException(409, "Already in favorites")
    fav = CandidateFavorite(candidate_id=current.id, job_id=job_id)
    db.add(fav); db.commit(); db.refresh(fav)
    return fav


@router.delete("/me/favorites/{job_id}", status_code=204)
def remove_favorite(
    job_id:  int,
    current: Candidate = Depends(get_current_candidate),
    db:      Session   = Depends(get_db),
):
    fav = db.query(CandidateFavorite).filter_by(candidate_id=current.id, job_id=job_id).first()
    if not fav: raise HTTPException(404, "Not in favorites")
    db.delete(fav); db.commit()


# ── STATS ──────────────────────────────────────────────────────────────────────

@router.get("/me/stats", response_model=CandidateStats)
def get_stats(current: Candidate = Depends(get_current_candidate), db: Session = Depends(get_db)):
    apps = db.query(CandidateApplication).filter(CandidateApplication.candidate_id == current.id).all()
    return CandidateStats(
        total_applications=len(apps),
        pending=  sum(1 for a in apps if a.status == AppStatus.pending),
        accepted= sum(1 for a in apps if a.status == AppStatus.accepted),
        rejected= sum(1 for a in apps if a.status == AppStatus.rejected),
        total_favorites= db.query(CandidateFavorite).filter_by(candidate_id=current.id).count(),
        total_documents= db.query(CandidateDocument).filter_by(candidate_id=current.id).count(),
    )
