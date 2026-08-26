"""Backward-compatible helpers; prefer app.modules.matching for new code."""

import os
import re
import smtplib
from email.message import EmailMessage

from app.models.recruitment import Job, Student
from app.modules.matching.pipeline import MatchingPipeline
from app.modules.matching.scorer import ApplicantProfile, JobProfile
from app.modules.matching.service import MatchingService


def split_skills(value: str | None) -> set[str]:
    if not value:
        return set()
    pieces = re.split(r"[,;\n|]+", value.lower())
    return {piece.strip() for piece in pieces if piece.strip()}


def candidate_match_score(
    student_skills: str | None, required_skills: str | None
) -> int:
    profile = ApplicantProfile(technical_skills=student_skills, skills=student_skills)
    job = JobProfile(title="role", description="", required_skills=required_skills)
    return MatchingPipeline.run(profile, job).compatibility_score


def candidate_match_score_for_entities(student: Student, job: Job) -> int:
    return MatchingService.compatibility_score(student, job)


def send_interview_email(to_email: str, subject: str, body: str) -> bool:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("SMTP_FROM", username or "noreply@example.com")

    if not host or not username or not password:
        print(f"[email:dev] to={to_email} subject={subject}\n{body}")
        return False

    message = EmailMessage()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(host, port) as smtp:
        smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(message)
    return True
