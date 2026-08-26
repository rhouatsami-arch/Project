"""Couche données — constantes et métadonnées PostgreSQL / stockage."""

from __future__ import annotations

# Tables PostgreSQL principales (schéma relationnel)
CORE_TABLES: tuple[str, ...] = (
    "students",
    "recruiters",
    "admins",
    "jobs",
    "applications",
    "saved_jobs",
)

PLATFORM_TABLES: tuple[str, ...] = (
    "meetings",
    "notifications",
    "interview_slots",
    "candidate_availabilities",
    "recommendation_history",
    "audit_logs",
)

# Colonnes CV sur students (métadonnées + texte extrait)
CV_DB_COLUMNS: tuple[str, ...] = (
    "cv_filename",
    "cv_path",
    "cv_extracted_text",
    "cv_extracted_at",
)

# Stockage fichiers CV
CV_UPLOAD_DIR = "uploads/cvs"
CV_MAX_BYTES = 5 * 1024 * 1024
CV_ALLOWED_EXTENSIONS: frozenset[str] = frozenset({".pdf", ".doc", ".docx", ".txt"})

# Tables de traçabilité
TRACE_TABLES: tuple[str, ...] = ("audit_logs", "recommendation_history")

DATA_LAYER_SUMMARY = (
    "PostgreSQL (relationnel) + fichiers CV (disque) "
    "+ audit_logs + recommendation_history"
)

__all__ = [
    "CORE_TABLES",
    "CV_ALLOWED_EXTENSIONS",
    "CV_DB_COLUMNS",
    "CV_MAX_BYTES",
    "CV_UPLOAD_DIR",
    "DATA_LAYER_SUMMARY",
    "PLATFORM_TABLES",
    "TRACE_TABLES",
]
