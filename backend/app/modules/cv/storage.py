import re
from pathlib import Path

ALLOWED_CV_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt"}
MAX_CV_BYTES = 5 * 1024 * 1024
CV_UPLOAD_ROOT = Path("uploads/cvs")


def validate_cv_file(filename: str, contents: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_CV_EXTENSIONS:
        raise ValueError("Only PDF, DOC, DOCX, or TXT files are supported")
    if len(contents) > MAX_CV_BYTES:
        raise ValueError("CV file must be 5MB or smaller")
    return suffix


def save_cv_file(owner_id: str, filename: str, contents: bytes) -> str:
    validate_cv_file(filename, contents)
    CV_UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^a-zA-Z0-9_.-]", "_", filename)
    path = CV_UPLOAD_ROOT / f"{owner_id}_{safe_name}"
    path.write_bytes(contents)
    return str(path)


def delete_cv_file(path: str | None) -> None:
    if not path:
        return
    file_path = Path(path)
    if file_path.is_file():
        file_path.unlink()
