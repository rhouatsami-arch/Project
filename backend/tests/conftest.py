"""Shared pytest fixtures — in-memory SQLite + FastAPI TestClient."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import hash_password
from app.database import Base, get_db
from app.main import app
from app.models import auth as auth_models  # noqa: F401 — register auth tables
from app.models import platform  # noqa: F401 — register platform tables
from app.models.recruitment import Job, JobStatus, Recruiter, Student


@pytest.fixture()
def db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    session_factory = sessionmaker(bind=db_engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_engine):
    session_factory = sessionmaker(bind=db_engine)

    def override_get_db():
        db = session_factory()
        try:
            yield db
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def sample_recruiter(db_session) -> Recruiter:
    recruiter = Recruiter(
        email="recruiter@test.com",
        hashed_password=hash_password("Password123"),
        first_name="Rec",
        last_name="Ruiter",
        company_name="Test Corp",
    )
    db_session.add(recruiter)
    db_session.commit()
    db_session.refresh(recruiter)
    return recruiter


@pytest.fixture()
def sample_student(db_session) -> Student:
    student = Student(
        email="student@test.com",
        hashed_password=hash_password("Password123"),
        first_name="Stu",
        last_name="Dent",
        university="Test University",
        field_of_study="Computer Science",
        technical_skills="python,sql,fastapi",
        skills="python,sql,fastapi",
        account_kind="student",
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


@pytest.fixture()
def sample_job(db_session, sample_recruiter) -> Job:
    job = Job(
        recruiter_id=sample_recruiter.id,
        title="Backend Developer",
        description="Build APIs with Python and FastAPI. 2 years experience required.",
        required_skills="python,fastapi|optional:docker,aws",
        location="Paris",
        employment_type="full_time",
        status=JobStatus.open,
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    return job


@pytest.fixture()
def auth_headers_student(client, sample_student) -> dict[str, str]:
    response = client.post(
        "/auth/login",
        data={"username": sample_student.email, "password": "Password123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
