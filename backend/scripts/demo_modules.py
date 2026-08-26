#!/usr/bin/env python3
"""Demo: users CRUD, offers CRUD, CV upload + raw text extraction."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.main import app  # noqa: E402

client = TestClient(app)
UPLOADS = ROOT / "uploads" / "cvs"


def section(title: str) -> None:
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


def ok(label: str, response) -> dict | list | None:
    print(f"{label}: {response.status_code}")
    if response.status_code >= 400:
        print(response.text)
        return None
    if response.content:
        try:
            data = response.json()
            print(json.dumps(data, indent=2, default=str)[:1200])
            return data
        except Exception:
            print(f"bytes={len(response.content)}")
    return None


def main() -> None:
    section("1. Health")
    ok("GET /", client.get("/"))

    stamp = "demo2026"
    recruiter_email = f"recruiter.{stamp}@example.com"
    student_email = f"student.{stamp}@example.com"

    section("2. Users — Create recruiter")
    ok(
        "POST /auth/recruiters/register",
        client.post(
            "/auth/recruiters/register",
            json={
                "email": recruiter_email,
                "password": "Password123",
                "first_name": "Leila",
                "last_name": "HR",
                "company_name": "Matious Corp",
            },
        ),
    )

    section("3. Users — Create student")
    ok(
        "POST /auth/students/register",
        client.post(
            "/auth/students/register",
            json={
                "email": student_email,
                "password": "Password123",
                "first_name": "Omar",
                "last_name": "Dev",
                "university": "ENSIAS",
                "field_of_study": "Software Engineering",
            },
        ),
    )

    section("4. Auth — Login")
    recruiter_login = ok(
        "POST /auth/login (recruiter)",
        client.post(
            "/auth/login",
            data={"username": recruiter_email, "password": "Password123"},
        ),
    )
    student_login = ok(
        "POST /auth/login (student)",
        client.post(
            "/auth/login",
            data={"username": student_email, "password": "Password123"},
        ),
    )
    if not recruiter_login or not student_login:
        sys.exit(1)

    recruiter_headers = {"Authorization": f"Bearer {recruiter_login['access_token']}"}
    student_headers = {"Authorization": f"Bearer {student_login['access_token']}"}

    section("5. Offers — CRUD")
    job = ok(
        "POST /jobs/",
        client.post(
            "/jobs/",
            headers=recruiter_headers,
            json={
                "title": "Python Backend Intern",
                "description": "FastAPI, PostgreSQL, REST APIs",
                "required_skills": "python, fastapi, postgresql, git",
                "location": "Casablanca",
                "employment_type": "internship",
            },
        ),
    )
    if not job:
        sys.exit(1)

    job_id = job["id"]
    ok("GET /jobs/", client.get("/jobs/"))
    ok("GET /jobs/{id}", client.get(f"/jobs/{job_id}"))
    ok(
        "PATCH /jobs/{id}",
        client.patch(
            f"/jobs/{job_id}",
            headers=recruiter_headers,
            json={"location": "Rabat"},
        ),
    )

    section("6. CV — Upload TXT + raw extraction")
    cv_text = (
        "Omar Dev\nSoftware Engineering student\n"
        "Skills: Python, FastAPI, React, PostgreSQL, Docker, Git\n"
        "Projects: Recruitment platform with Next.js and FastAPI\n"
    )
    cv_path = ROOT / "demo_cv.txt"
    cv_path.write_text(cv_text, encoding="utf-8")

    ok(
        "POST /students/me/cv",
        client.post(
            "/students/me/cv",
            headers=student_headers,
            files={"file": ("demo_cv.txt", cv_text.encode("utf-8"), "text/plain")},
        ),
    )

    if extracted := ok(
        "GET /students/me/cv/extracted",
        client.get("/students/me/cv/extracted", headers=student_headers),
    ):
        print(f"\nRaw text length: {extracted['char_count']} chars")
        print(f"Skills detected: {extracted['skills_detected']}")

    ok(
        "GET /students/me/cv/download",
        client.get("/students/me/cv/download", headers=student_headers),
    )

    section("7. Users — Update profile")
    ok(
        "PATCH /students/me",
        client.patch(
            "/students/me",
            headers=student_headers,
            json={"bio": "Backend-focused student open to internships."},
        ),
    )

    section("8. Apply + recruiter reads CV text")
    if apply := ok(
        "POST /students/jobs/{id}/apply",
        client.post(
            f"/students/jobs/{job_id}/apply",
            headers=student_headers,
            json={"cover_letter": "Interested in this role."},
        ),
    ):
        ok(
            "GET /recruiters/applications/{id}/cv/extracted",
            client.get(
                f"/recruiters/applications/{apply['id']}/cv/extracted",
                headers=recruiter_headers,
            ),
        )

    section("9. Cleanup demo offer")
    ok("DELETE /jobs/{id}", client.delete(f"/jobs/{job_id}", headers=recruiter_headers))

    print("\nDemo complete. Open http://127.0.0.1:8000/docs for Swagger UI.")
    if UPLOADS.exists():
        print(f"CV files stored under: {UPLOADS}")


if __name__ == "__main__":
    main()
