"""
app/services/cv_storage.py
----------------------------
Storage abstraction layer. Currently uses local filesystem.
Swap _save_to_disk / _read_from_disk for S3/Azure Blob later without
touching router code.
"""
import os
import uuid
import datetime

CV_STORAGE_ROOT = "uploads/cvs"


def generate_storage_path(owner_id: str, ext: str) -> str:
    """Unique, collision-proof storage path per upload."""
    date_prefix = datetime.datetime.utcnow().strftime("%Y%m")
    unique_id   = uuid.uuid4().hex[:8]
    folder = os.path.join(CV_STORAGE_ROOT, date_prefix)
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, f"{owner_id}_{unique_id}.{ext}")


def save_file(file_bytes: bytes, path: str) -> None:
    with open(path, "wb") as f:
        f.write(file_bytes)


def delete_file(path: str) -> bool:
    if path and os.path.exists(path):
        os.remove(path)
        return True
    return False


def read_file(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()
