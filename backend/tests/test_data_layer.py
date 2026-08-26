"""Tests — métadonnées couche données."""

from app.modules.platform.data_layer import (
    CORE_TABLES,
    CV_DB_COLUMNS,
    TRACE_TABLES,
)


def test_core_tables_include_business_entities():
    assert "students" in CORE_TABLES
    assert "jobs" in CORE_TABLES
    assert "applications" in CORE_TABLES


def test_trace_tables_include_audit_and_history():
    assert "audit_logs" in TRACE_TABLES
    assert "recommendation_history" in TRACE_TABLES


def test_cv_db_columns_cover_hybrid_storage():
    assert "cv_path" in CV_DB_COLUMNS
    assert "cv_extracted_text" in CV_DB_COLUMNS
