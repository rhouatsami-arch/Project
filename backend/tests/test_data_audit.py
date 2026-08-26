"""Tests — journaux d'audit (couche données)."""

from app.models.platform import AuditLog
from app.modules.platform.audit import ACTION_LABELS, AuditAction, record_audit


def test_record_audit_persists_log(db_session):
    log = record_audit(
        db_session,
        actor_email="admin@matioushire.com",
        actor_role="admin",
        action=AuditAction.LOGIN,
        resource="session",
        details="Connexion réussie",
    )
    db_session.commit()

    assert log.id is not None
    assert log.actor_email == "admin@matioushire.com"
    assert log.action == AuditAction.LOGIN
    assert log.details == "Connexion réussie"

    stored = db_session.query(AuditLog).filter(AuditLog.id == log.id).first()
    assert stored is not None
    assert stored.actor_role == "admin"


def test_audit_action_labels_cover_key_actions():
    assert ACTION_LABELS[AuditAction.UPLOAD_CV] == "Upload CV"
    assert ACTION_LABELS[AuditAction.RANK_CANDIDATES] == "Classement candidats"
    assert ACTION_LABELS[AuditAction.APPLY_JOB] == "Candidature"
