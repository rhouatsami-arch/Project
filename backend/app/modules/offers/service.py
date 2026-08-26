from sqlalchemy.orm import Session

from app.models.recruitment import Job, JobStatus, Recruiter


class OfferService:
    """CRUD helpers for job offers (offres)."""

    @staticmethod
    def list_open(
        db: Session,
        *,
        search: str | None = None,
        location: str | None = None,
        skill: str | None = None,
        employment_type: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Job]:
        from sqlalchemy import or_

        query = db.query(Job).filter(Job.status == JobStatus.open)
        if search:
            query = query.filter(
                or_(
                    Job.title.ilike(f"%{search}%"), Job.description.ilike(f"%{search}%")
                )
            )
        if location:
            query = query.filter(Job.location.ilike(f"%{location}%"))
        if skill:
            query = query.filter(Job.required_skills.ilike(f"%{skill}%"))
        if employment_type:
            query = query.filter(Job.employment_type == employment_type)
        return query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_open(db: Session, job_id: int) -> Job | None:
        return (
            db.query(Job).filter(Job.id == job_id, Job.status == JobStatus.open).first()
        )

    @staticmethod
    def list_for_recruiter(db: Session, recruiter_id) -> list[Job]:
        return (
            db.query(Job)
            .filter(Job.recruiter_id == recruiter_id)
            .order_by(Job.created_at.desc())
            .all()
        )

    @staticmethod
    def create(db: Session, recruiter: Recruiter, data: dict) -> Job:
        job = Job(recruiter_id=recruiter.id, **data)
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def update(db: Session, job: Job, data: dict) -> Job:
        for field, value in data.items():
            setattr(job, field, value)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def delete(db: Session, job: Job) -> None:
        db.delete(job)
        db.commit()
