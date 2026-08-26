"""Central audit logging for MatiousHire platform actions."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.platform import AuditLog
from app.modules.platform.service import AuditService


class AuditAction:
    LOGIN = "login"
    REGISTER_STUDENT = "register_student"
    REGISTER_CANDIDATE = "register_candidate"
    REGISTER_RECRUITER = "register_recruiter"
    REGISTER_ADMIN = "register_admin"

    UPDATE_PROFILE = "update_profile"
    DELETE_PROFILE = "delete_profile"

    APPLY_JOB = "apply_job"
    UPLOAD_CV = "upload_cv"
    DELETE_CV = "delete_cv"

    CREATE_JOB = "create_job"
    UPDATE_JOB = "update_job"
    DELETE_JOB = "delete_job"

    SHORTLIST_APPLICATION = "shortlist_application"
    REJECT_APPLICATION = "reject_application"
    HIRE_APPLICATION = "hire_application"
    INVITE_INTERVIEW = "invite_interview"

    CREATE_INTERVIEW_SLOT = "create_interview_slot"
    DELETE_INTERVIEW_SLOT = "delete_interview_slot"
    ADD_AVAILABILITY = "add_availability"
    DELETE_AVAILABILITY = "delete_availability"
    SCHEDULE_MEETING = "schedule_meeting"
    PROPOSE_MEETING = "propose_meeting"
    CONFIRM_MEETING = "confirm_meeting"
    REFUSE_MEETING = "refuse_meeting"
    CANCEL_MEETING = "cancel_meeting"
    RESCHEDULE_MEETING = "reschedule_meeting"
    COMPLETE_MEETING = "complete_meeting"

    RUN_MATCHING_SCORE = "run_matching_score"
    RANK_CANDIDATES = "rank_candidates"

    CREATE_STUDENT = "create_student"
    CREATE_CANDIDATE = "create_candidate"
    CREATE_RECRUITER = "create_recruiter"
    DELETE_STUDENT = "delete_student"
    DELETE_CANDIDATE = "delete_candidate"
    DELETE_RECRUITER = "delete_recruiter"


ACTION_LABELS: dict[str, str] = {
    AuditAction.LOGIN: "Connexion",
    AuditAction.REGISTER_STUDENT: "Inscription étudiant",
    AuditAction.REGISTER_CANDIDATE: "Inscription candidat",
    AuditAction.REGISTER_RECRUITER: "Inscription recruteur",
    AuditAction.REGISTER_ADMIN: "Inscription administrateur",
    AuditAction.UPDATE_PROFILE: "Mise à jour profil",
    AuditAction.DELETE_PROFILE: "Suppression profil",
    AuditAction.APPLY_JOB: "Candidature",
    AuditAction.UPLOAD_CV: "Upload CV",
    AuditAction.DELETE_CV: "Suppression CV",
    AuditAction.CREATE_JOB: "Création offre",
    AuditAction.UPDATE_JOB: "Mise à jour offre",
    AuditAction.DELETE_JOB: "Suppression offre",
    AuditAction.SHORTLIST_APPLICATION: "Shortlist candidature",
    AuditAction.REJECT_APPLICATION: "Rejet candidature",
    AuditAction.HIRE_APPLICATION: "Recrutement candidat",
    AuditAction.INVITE_INTERVIEW: "Invitation entretien",
    AuditAction.CREATE_INTERVIEW_SLOT: "Créneau entretien créé",
    AuditAction.DELETE_INTERVIEW_SLOT: "Créneau entretien supprimé",
    AuditAction.ADD_AVAILABILITY: "Disponibilité ajoutée",
    AuditAction.DELETE_AVAILABILITY: "Disponibilité supprimée",
    AuditAction.SCHEDULE_MEETING: "Entretien planifié",
    AuditAction.PROPOSE_MEETING: "Entretien proposé",
    AuditAction.CONFIRM_MEETING: "Entretien confirmé",
    AuditAction.REFUSE_MEETING: "Entretien refusé",
    AuditAction.CANCEL_MEETING: "Entretien annulé",
    AuditAction.RESCHEDULE_MEETING: "Entretien replanifié",
    AuditAction.COMPLETE_MEETING: "Entretien terminé",
    AuditAction.RUN_MATCHING_SCORE: "Calcul score matching",
    AuditAction.RANK_CANDIDATES: "Classement candidats",
    AuditAction.CREATE_STUDENT: "Création étudiant (admin)",
    AuditAction.CREATE_CANDIDATE: "Création candidat (admin)",
    AuditAction.CREATE_RECRUITER: "Création recruteur (admin)",
    AuditAction.DELETE_STUDENT: "Suppression étudiant (admin)",
    AuditAction.DELETE_CANDIDATE: "Suppression candidat (admin)",
    AuditAction.DELETE_RECRUITER: "Suppression recruteur (admin)",
}


def record_audit(
    db: Session,
    *,
    actor_email: str,
    actor_role: str,
    action: str,
    resource: str | None = None,
    details: str | None = None,
) -> AuditLog:
    return AuditService.log(
        db,
        actor_email=actor_email,
        actor_role=actor_role,
        action=action,
        resource=resource,
        details=details,
    )


def audit_to_dict(log: AuditLog) -> dict[str, object]:
    return {
        "id": log.id,
        "actor_email": log.actor_email,
        "actor_role": log.actor_role,
        "action": log.action,
        "action_label": ACTION_LABELS.get(log.action, log.action),
        "resource": log.resource,
        "details": log.details,
        "created_at": log.created_at.isoformat(),
    }
