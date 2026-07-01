from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.application import Application, AppStatus

router = APIRouter(prefix="/applications", tags=["applications"])

@router.post("/")
def apply(job_id: int, student_id: int, db: Session = Depends(get_db)):
    app = Application(student_id=student_id, job_id=job_id)
    db.add(app); db.commit(); db.refresh(app)
    return app

@router.patch("/{app_id}/status")
def update_status(app_id: int, status: AppStatus, db: Session = Depends(get_db)):
    app = db.query(Application).filter(Application.id == app_id).first()
    app.status = status; db.commit()
    return app