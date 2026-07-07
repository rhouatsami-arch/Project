import os
import re
import smtplib
import zipfile
from email.message import EmailMessage
from html import unescape
from pathlib import Path


SKILL_KEYWORDS = {
    "python", "java", "javascript", "typescript", "react", "vue", "angular",
    "node", "express", "fastapi", "django", "flask", "sql", "postgresql",
    "mysql", "mongodb", "docker", "kubernetes", "git", "linux", "aws",
    "azure", "gcp", "machine learning", "data analysis", "excel", "power bi",
    "tableau", "html", "css", "figma", "rest api", "graphql", "testing",
    "communication", "leadership", "project management", "scrum", "agile",
}


def split_skills(value: str | None) -> set[str]:
    if not value:
        return set()
    pieces = re.split(r"[,;\n|]+", value.lower())
    return {piece.strip() for piece in pieces if piece.strip()}


def extract_text_from_upload(filename: str, contents: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".docx":
        return _extract_docx_text(contents)
    return contents.decode("utf-8", errors="ignore")


def extract_skills(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text.lower())
    found = {skill for skill in SKILL_KEYWORDS if re.search(rf"\b{re.escape(skill)}\b", normalized)}
    return sorted(found)


def save_cv(student_id: str, filename: str, contents: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in {".pdf", ".doc", ".docx", ".txt"}:
        raise ValueError("Only PDF, DOC, DOCX, or TXT files are supported")
    if len(contents) > 5 * 1024 * 1024:
        raise ValueError("CV file must be 5MB or smaller")

    root = Path("uploads/cvs")
    root.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", filename)
    path = root / f"{student_id}_{safe_name}"
    path.write_bytes(contents)
    return str(path)


def candidate_match_score(student_skills: str | None, required_skills: str | None) -> int:
    required = split_skills(required_skills)
    if not required:
        return 0
    student = split_skills(student_skills)
    if not student:
        return 0
    return round(len(student & required) / len(required) * 100)


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


def _extract_docx_text(contents: bytes) -> str:
    from io import BytesIO

    try:
        with zipfile.ZipFile(BytesIO(contents)) as docx:
            xml = docx.read("word/document.xml").decode("utf-8", errors="ignore")
    except Exception:
        return ""
    text = re.sub(r"<[^>]+>", " ", xml)
    return unescape(re.sub(r"\s+", " ", text))
