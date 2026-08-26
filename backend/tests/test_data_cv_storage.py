"""Tests — stockage fichiers CV (couche données)."""

from pathlib import Path

import pytest

from app.modules.cv import storage


@pytest.fixture()
def cv_upload_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "CV_UPLOAD_ROOT", tmp_path)
    return tmp_path


def test_validate_cv_file_accepts_pdf():
    assert storage.validate_cv_file("resume.pdf", b"%PDF-1.4 content") == ".pdf"


def test_validate_cv_file_rejects_unsupported_extension():
    with pytest.raises(ValueError, match="Only PDF"):
        storage.validate_cv_file("resume.exe", b"binary")


def test_validate_cv_file_rejects_oversized_file():
    huge = b"x" * (storage.MAX_CV_BYTES + 1)
    with pytest.raises(ValueError, match="5MB"):
        storage.validate_cv_file("resume.pdf", huge)


def test_save_and_delete_cv_file(cv_upload_dir):
    contents = b"Python developer CV content"
    path = storage.save_cv_file("user-123", "My CV.pdf", contents)

    file_path = Path(path)
    assert file_path.is_file()
    assert file_path.read_bytes() == contents
    assert file_path.parent == cv_upload_dir

    storage.delete_cv_file(path)
    assert not file_path.is_file()


def test_delete_cv_file_handles_missing_path():
    storage.delete_cv_file(None)
    storage.delete_cv_file("/nonexistent/path/cv.pdf")
