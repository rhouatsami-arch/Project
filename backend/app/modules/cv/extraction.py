import re
import zipfile
from html import unescape
from io import BytesIO
from pathlib import Path


def extract_raw_text(filename: str, contents: bytes) -> str:
    """Extract plain text from CV bytes (PDF, DOCX, TXT)."""
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf_text(contents)
    if suffix == ".docx":
        return _extract_docx_text(contents)
    if suffix == ".txt":
        return contents.decode("utf-8", errors="ignore").strip()
    # Legacy .doc: best-effort UTF-8 decode
    return contents.decode("utf-8", errors="ignore").strip()


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _extract_pdf_text(contents: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        return contents.decode("utf-8", errors="ignore").strip()

    try:
        reader = PdfReader(BytesIO(contents))
        pages = [page.extract_text() or "" for page in reader.pages]
        return normalize_text("\n".join(pages))
    except Exception:
        return ""


def _extract_docx_text(contents: bytes) -> str:
    try:
        with zipfile.ZipFile(BytesIO(contents)) as docx:
            xml = docx.read("word/document.xml").decode("utf-8", errors="ignore")
    except Exception:
        return ""
    text = re.sub(r"<[^>]+>", " ", xml)
    return normalize_text(unescape(text))
