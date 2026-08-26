"""Auth registration/login edge cases."""

from __future__ import annotations

from app.auth import hash_password
from app.models.recruitment import Student


def test_login_is_case_insensitive_for_email(client, db_session, sample_student):
    sample_student.email = "Student.Test@Example.com"
    db_session.commit()

    response = client.post(
        "/auth/login",
        data={"username": "student.test@example.com", "password": "Password123"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "student"


def test_candidate_register_upgrades_existing_student(client, db_session):
    student = Student(
        email="upgrade.me@example.com",
        hashed_password=hash_password("Password123"),
        first_name="Old",
        last_name="Name",
        university="Old Uni",
        field_of_study="CS",
        skills="python",
        technical_skills="python",
        account_kind="student",
    )
    db_session.add(student)
    db_session.commit()

    response = client.post(
        "/auth/candidates/register",
        json={
            "email": "Upgrade.Me@Example.com",
            "password": "Password123",
            "first_name": "Najib",
            "last_name": "Lemsellak",
            "university": "Um6sp",
            "field_of_study": "Data analyst",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["account_kind"] == "candidate"
    assert body["first_name"] == "Najib"

    login = client.post(
        "/auth/login",
        data={
            "username": "upgrade.me@example.com",
            "password": "Password123",
            "client_id": "candidate",
        },
    )
    assert login.status_code == 200
    assert login.json()["role"] == "candidate"


def test_duplicate_candidate_register_returns_helpful_message(client, db_session):
    student = Student(
        email="already.candidate@example.com",
        hashed_password=hash_password("Password123"),
        first_name="Cand",
        last_name="Idate",
        university="Uni",
        field_of_study="Data",
        skills="sql",
        technical_skills="sql",
        account_kind="candidate",
    )
    db_session.add(student)
    db_session.commit()

    response = client.post(
        "/auth/candidates/register",
        json={
            "email": "already.candidate@example.com",
            "password": "Password123",
            "first_name": "Najib",
            "last_name": "Lemsellak",
            "university": "Um6sp",
            "field_of_study": "Data analyst",
        },
    )
    assert response.status_code == 409
    payload = response.json()
    message = payload.get("detail") or payload.get("error", {}).get("message", "")
    assert "sign in" in str(message).lower()
