from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from app.models.platform import (
    AuditLog,
    CandidateAvailability,
    InterviewSlot,
    Meeting,
    MeetingStatus,
    Notification,
    NotificationType,
)
from app.models.recruitment import Application, ApplicationStatus, Recruiter, Student
from app.services.recruitment_legacy import send_interview_email
from app.utils.datetime import utc_now


class NotificationService:
    @staticmethod
    def notify(
        db: Session,
        *,
        user_email: str,
        user_role: str,
        type: NotificationType,
        title: str,
        message: str,
        also_email: bool = False,
        email_subject: str | None = None,
    ) -> Notification:
        item = Notification(
            user_email=user_email,
            user_role=user_role,
            type=type,
            title=title,
            message=message,
        )
        db.add(item)
        if also_email:
            send_interview_email(
                to_email=user_email,
                subject=email_subject or title,
                body=message,
            )
        return item


def _overlap_seconds(
    a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime
) -> float:
    start = max(a_start, b_start)
    end = min(a_end, b_end)
    if end <= start:
        return 0.0
    return (end - start).total_seconds()


def _candidate_role(student: Student) -> str:
    return getattr(student, "role", None) or "candidate"


class MeetingService:
    @staticmethod
    def create_slot(
        db: Session,
        *,
        recruiter: Recruiter,
        starts_at: datetime,
        ends_at: datetime,
    ) -> InterviewSlot:
        if ends_at <= starts_at:
            raise ValueError("ends_at must be after starts_at")
        slot = InterviewSlot(
            recruiter_id=recruiter.id,
            starts_at=starts_at,
            ends_at=ends_at,
            is_booked=False,
        )
        db.add(slot)
        return slot

    @staticmethod
    def list_slots(db: Session, recruiter: Recruiter) -> list[InterviewSlot]:
        return (
            db.query(InterviewSlot)
            .filter(InterviewSlot.recruiter_id == recruiter.id)
            .order_by(InterviewSlot.starts_at.asc())
            .all()
        )

    @staticmethod
    def delete_slot(db: Session, *, recruiter: Recruiter, slot_id: int) -> None:
        slot = (
            db.query(InterviewSlot)
            .filter(
                InterviewSlot.id == slot_id,
                InterviewSlot.recruiter_id == recruiter.id,
            )
            .first()
        )
        if not slot:
            raise LookupError("Slot not found")
        if slot.is_booked:
            raise ValueError("Cannot delete a booked slot")
        db.delete(slot)

    @staticmethod
    def add_availability(
        db: Session,
        *,
        student: Student,
        starts_at: datetime,
        ends_at: datetime,
    ) -> CandidateAvailability:
        if ends_at <= starts_at:
            raise ValueError("ends_at must be after starts_at")
        window = CandidateAvailability(
            student_id=student.id,
            starts_at=starts_at,
            ends_at=ends_at,
        )
        db.add(window)
        return window

    @staticmethod
    def list_availability(db: Session, student: Student) -> list[CandidateAvailability]:
        return (
            db.query(CandidateAvailability)
            .filter(CandidateAvailability.student_id == student.id)
            .order_by(CandidateAvailability.starts_at.asc())
            .all()
        )

    @staticmethod
    def delete_availability(
        db: Session, *, student: Student, availability_id: int
    ) -> None:
        window = (
            db.query(CandidateAvailability)
            .filter(
                CandidateAvailability.id == availability_id,
                CandidateAvailability.student_id == student.id,
            )
            .first()
        )
        if not window:
            raise LookupError("Availability not found")
        db.delete(window)

    @staticmethod
    def find_best_slot(
        db: Session,
        *,
        recruiter: Recruiter,
        student: Student,
    ) -> InterviewSlot | None:
        slots = (
            db.query(InterviewSlot)
            .filter(
                InterviewSlot.recruiter_id == recruiter.id,
                InterviewSlot.is_booked.is_(False),
                InterviewSlot.starts_at >= utc_now(),
            )
            .order_by(InterviewSlot.starts_at.asc())
            .all()
        )
        windows = MeetingService.list_availability(db, student)
        if not slots:
            return None
        if not windows:
            return slots[0]

        best: InterviewSlot | None = None
        best_score = -1.0
        for slot in slots:
            for window in windows:
                overlap = _overlap_seconds(
                    slot.starts_at, slot.ends_at, window.starts_at, window.ends_at
                )
                if overlap <= 0:
                    continue
                # Prefer full containment, then longer overlap, then earlier start
                contained = (
                    slot.starts_at >= window.starts_at
                    and slot.ends_at <= window.ends_at
                )
                score = overlap + (1_000_000 if contained else 0)
                if score > best_score:
                    best_score = score
                    best = slot
        return best

    @staticmethod
    def propose_best(
        db: Session,
        *,
        application: Application,
        recruiter: Recruiter,
        location: str | None = None,
        notes: str | None = None,
        slot_id: int | None = None,
    ) -> Meeting:
        application = (
            db.query(Application)
            .options(joinedload(Application.job), joinedload(Application.student))
            .filter(Application.id == application.id)
            .first()
        )
        if not application:
            raise LookupError("Application not found")

        if slot_id is not None:
            slot = (
                db.query(InterviewSlot)
                .filter(
                    InterviewSlot.id == slot_id,
                    InterviewSlot.recruiter_id == recruiter.id,
                    InterviewSlot.is_booked.is_(False),
                )
                .first()
            )
            if not slot:
                raise LookupError("Free slot not found")
        else:
            slot = MeetingService.find_best_slot(
                db, recruiter=recruiter, student=application.student
            )
            if not slot:
                raise LookupError(
                    "No overlapping free slot found. Add recruiter slots "
                    "and/or candidate availability."
                )

        meeting = Meeting(
            application_id=application.id,
            recruiter_id=recruiter.id,
            student_id=application.student_id,
            job_id=application.job_id,
            slot_id=slot.id,
            scheduled_at=slot.starts_at,
            location=location,
            notes=notes or "Proposition automatique du meilleur créneau commun.",
            status=MeetingStatus.proposed.value,
            updated_at=utc_now(),
        )
        slot.is_booked = True
        application.status = ApplicationStatus.interview_invited
        application.interview_at = slot.starts_at
        db.add(meeting)

        title = "Entretien proposé"
        message = (
            f"Un créneau d'entretien vous est proposé pour "
            f"{application.job.title} le {slot.starts_at.isoformat()}. "
            f"Statut : proposée. Merci de confirmer ou refuser."
        )
        NotificationService.notify(
            db,
            user_email=application.student.email,
            user_role=_candidate_role(application.student),
            type=NotificationType.interview,
            title=title,
            message=message,
            also_email=True,
            email_subject=f"Proposition d'entretien — {application.job.title}",
        )
        return meeting

    @staticmethod
    def schedule(
        db: Session,
        *,
        application: Application,
        recruiter: Recruiter,
        scheduled_at,
        location: str | None = None,
        notes: str | None = None,
    ) -> Meeting:
        meeting = Meeting(
            application_id=application.id,
            recruiter_id=recruiter.id,
            student_id=application.student_id,
            job_id=application.job_id,
            scheduled_at=scheduled_at,
            location=location,
            notes=notes,
            status=MeetingStatus.proposed.value,
            updated_at=utc_now(),
        )
        db.add(meeting)
        application.status = ApplicationStatus.interview_invited
        application.interview_at = scheduled_at
        NotificationService.notify(
            db,
            user_email=application.student.email,
            user_role=_candidate_role(application.student),
            type=NotificationType.interview,
            title="Entretien proposé",
            message=(
                f"Un entretien a été proposé pour {application.job.title} "
                f"le {scheduled_at.isoformat()}. Statut : proposée."
            ),
            also_email=True,
            email_subject=f"Proposition d'entretien — {application.job.title}",
        )
        return meeting

    @staticmethod
    def _get_meeting(db: Session, meeting_id: int) -> Meeting:
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            raise LookupError("Meeting not found")
        return meeting

    @staticmethod
    def _release_slot(db: Session, meeting: Meeting) -> None:
        if not meeting.slot_id:
            return
        slot = (
            db.query(InterviewSlot).filter(InterviewSlot.id == meeting.slot_id).first()
        )
        if slot:
            slot.is_booked = False

    @staticmethod
    def confirm(db: Session, *, meeting_id: int, student: Student) -> Meeting:
        meeting = MeetingService._get_meeting(db, meeting_id)
        if meeting.student_id != student.id:
            raise PermissionError("Not your meeting")
        if meeting.status not in {
            MeetingStatus.proposed.value,
            MeetingStatus.refused.value,
        }:
            raise ValueError("Meeting cannot be confirmed in its current status")
        meeting.status = MeetingStatus.accepted.value
        meeting.updated_at = utc_now()
        recruiter = (
            db.query(Recruiter).filter(Recruiter.id == meeting.recruiter_id).first()
        )
        if recruiter:
            NotificationService.notify(
                db,
                user_email=recruiter.email,
                user_role="recruiter",
                type=NotificationType.interview,
                title="Entretien accepté",
                message=(
                    f"{student.first_name} {student.last_name} a accepté "
                    f"l'entretien du {meeting.scheduled_at.isoformat()}."
                ),
                also_email=True,
                email_subject="Entretien accepté par le candidat",
            )
        return meeting

    @staticmethod
    def refuse(db: Session, *, meeting_id: int, student: Student) -> Meeting:
        meeting = MeetingService._get_meeting(db, meeting_id)
        if meeting.student_id != student.id:
            raise PermissionError("Not your meeting")
        if meeting.status != MeetingStatus.proposed.value:
            raise ValueError("Only proposed meetings can be refused")
        meeting.status = MeetingStatus.refused.value
        meeting.updated_at = utc_now()
        MeetingService._release_slot(db, meeting)
        meeting.slot_id = None
        recruiter = (
            db.query(Recruiter).filter(Recruiter.id == meeting.recruiter_id).first()
        )
        if recruiter:
            NotificationService.notify(
                db,
                user_email=recruiter.email,
                user_role="recruiter",
                type=NotificationType.interview,
                title="Entretien refusé",
                message=(
                    f"{student.first_name} {student.last_name} a refusé "
                    f"l'entretien du {meeting.scheduled_at.isoformat()}."
                ),
                also_email=True,
                email_subject="Entretien refusé par le candidat",
            )
        return meeting

    @staticmethod
    def cancel(
        db: Session,
        *,
        meeting_id: int,
        actor_recruiter: Recruiter | None = None,
        actor_student: Student | None = None,
    ) -> Meeting:
        meeting = MeetingService._get_meeting(db, meeting_id)
        if actor_recruiter and meeting.recruiter_id != actor_recruiter.id:
            raise PermissionError("Not your meeting")
        if actor_student and meeting.student_id != actor_student.id:
            raise PermissionError("Not your meeting")
        if meeting.status in {
            MeetingStatus.completed.value,
            MeetingStatus.cancelled.value,
        }:
            raise ValueError("Meeting already closed")
        meeting.status = MeetingStatus.cancelled.value
        meeting.updated_at = utc_now()
        MeetingService._release_slot(db, meeting)
        meeting.slot_id = None

        student = db.query(Student).filter(Student.id == meeting.student_id).first()
        recruiter = (
            db.query(Recruiter).filter(Recruiter.id == meeting.recruiter_id).first()
        )
        cancel_msg = f"L'entretien du {meeting.scheduled_at.isoformat()} a été annulé."
        if student and actor_recruiter:
            NotificationService.notify(
                db,
                user_email=student.email,
                user_role=_candidate_role(student),
                type=NotificationType.interview,
                title="Entretien annulé",
                message=cancel_msg,
                also_email=True,
                email_subject="Entretien annulé",
            )
        if recruiter and actor_student:
            NotificationService.notify(
                db,
                user_email=recruiter.email,
                user_role="recruiter",
                type=NotificationType.interview,
                title="Entretien annulé",
                message=cancel_msg,
                also_email=True,
                email_subject="Entretien annulé",
            )
        return meeting

    @staticmethod
    def reschedule(
        db: Session,
        *,
        meeting_id: int,
        recruiter: Recruiter,
        scheduled_at: datetime | None = None,
        slot_id: int | None = None,
        location: str | None = None,
        notes: str | None = None,
    ) -> Meeting:
        meeting = MeetingService._get_meeting(db, meeting_id)
        if meeting.recruiter_id != recruiter.id:
            raise PermissionError("Not your meeting")
        if meeting.status in {
            MeetingStatus.completed.value,
            MeetingStatus.cancelled.value,
        }:
            raise ValueError("Cannot reschedule a closed meeting")

        MeetingService._release_slot(db, meeting)
        new_slot: InterviewSlot | None = None
        if slot_id is not None:
            new_slot = (
                db.query(InterviewSlot)
                .filter(
                    InterviewSlot.id == slot_id,
                    InterviewSlot.recruiter_id == recruiter.id,
                    InterviewSlot.is_booked.is_(False),
                )
                .first()
            )
            if not new_slot:
                raise LookupError("Free slot not found")
            meeting.slot_id = new_slot.id
            meeting.scheduled_at = new_slot.starts_at
            new_slot.is_booked = True
        elif scheduled_at is not None:
            meeting.slot_id = None
            meeting.scheduled_at = scheduled_at
        else:
            raise ValueError("Provide slot_id or scheduled_at")

        if location is not None:
            meeting.location = location
        if notes is not None:
            meeting.notes = notes
        meeting.status = MeetingStatus.proposed.value
        meeting.updated_at = utc_now()

        student = db.query(Student).filter(Student.id == meeting.student_id).first()
        if student:
            NotificationService.notify(
                db,
                user_email=student.email,
                user_role=_candidate_role(student),
                type=NotificationType.interview,
                title="Entretien reprogrammé",
                message=(
                    f"Un nouvel horaire vous est proposé : "
                    f"{meeting.scheduled_at.isoformat()}. Statut : proposée."
                ),
                also_email=True,
                email_subject="Entretien reprogrammé",
            )
        return meeting

    @staticmethod
    def complete(db: Session, *, meeting_id: int, recruiter: Recruiter) -> Meeting:
        meeting = MeetingService._get_meeting(db, meeting_id)
        if meeting.recruiter_id != recruiter.id:
            raise PermissionError("Not your meeting")
        if meeting.status != MeetingStatus.accepted.value:
            raise ValueError("Only accepted meetings can be marked completed")
        meeting.status = MeetingStatus.completed.value
        meeting.updated_at = utc_now()
        return meeting

    @staticmethod
    def list_for_recruiter(db: Session, recruiter: Recruiter) -> list[Meeting]:
        return (
            db.query(Meeting)
            .filter(Meeting.recruiter_id == recruiter.id)
            .order_by(Meeting.scheduled_at.desc())
            .all()
        )

    @staticmethod
    def list_for_student(db: Session, student: Student) -> list[Meeting]:
        return (
            db.query(Meeting)
            .filter(Meeting.student_id == student.id)
            .order_by(Meeting.scheduled_at.desc())
            .all()
        )


class AuditService:
    @staticmethod
    def log(
        db: Session,
        *,
        actor_email: str,
        actor_role: str,
        action: str,
        resource: str | None = None,
        details: str | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            actor_email=actor_email,
            actor_role=actor_role,
            action=action,
            resource=resource,
            details=details,
        )
        db.add(entry)
        return entry
