"""Sync MatiousHire meetings with Google Calendar events."""

from __future__ import annotations

import logging
import os
from datetime import timedelta

from sqlalchemy.orm import Session

from app.models.platform import GoogleCalendarConnection, InterviewSlot, Meeting
from app.models.recruitment import Job, Recruiter, Student
from app.modules.platform.google_calendar_service import (
    GoogleCalendarService,
    extract_meet_link,
    is_calendar_configured,
    token_expires_at,
)
from app.utils.datetime import utc_now

logger = logging.getLogger(__name__)


class MeetingCalendarSync:
    @staticmethod
    def sync_on_accepted(db: Session, meeting: Meeting) -> None:
        if meeting.status != "accepted":
            return
        if meeting.google_event_id:
            MeetingCalendarSync._update_event(db, meeting)
            return
        MeetingCalendarSync._create_event(db, meeting)

    @staticmethod
    def sync_on_rescheduled(db: Session, meeting: Meeting) -> None:
        if not meeting.google_event_id:
            return
        if meeting.status == "proposed":
            MeetingCalendarSync._cancel_event(db, meeting)
            meeting.google_event_id = None
            meeting.google_event_link = None
            meeting.google_meet_link = None
            return
        MeetingCalendarSync._update_event(db, meeting)

    @staticmethod
    def sync_on_cancelled(db: Session, meeting: Meeting) -> None:
        if not meeting.google_event_id:
            return
        MeetingCalendarSync._cancel_event(db, meeting)
        meeting.google_event_id = None
        meeting.google_event_link = None
        meeting.google_meet_link = None

    @staticmethod
    def _resolve_access(db: Session, recruiter_id) -> tuple[str, str] | None:
        if not is_calendar_configured():
            return None

        connection = (
            db.query(GoogleCalendarConnection)
            .filter(GoogleCalendarConnection.recruiter_id == recruiter_id)
            .first()
        )
        refresh_token = os.getenv("GOOGLE_CALENDAR_REFRESH_TOKEN", "").strip()
        calendar_id = "primary"

        if connection:
            refresh_token = connection.refresh_token
            calendar_id = connection.calendar_id or "primary"
            access_token = connection.access_token
            if access_token and connection.token_expires_at:
                if connection.token_expires_at > utc_now():
                    return access_token, calendar_id
            try:
                token_data = GoogleCalendarService.refresh_access_token(refresh_token)
            except Exception as exc:
                logger.warning("Google Calendar token refresh failed: %s", exc)
                return None
            access_token = token_data["access_token"]
            connection.access_token = access_token
            connection.token_expires_at = token_expires_at(token_data.get("expires_in"))
            connection.updated_at = utc_now()
            return access_token, calendar_id

        if refresh_token:
            try:
                token_data = GoogleCalendarService.refresh_access_token(refresh_token)
            except Exception as exc:
                logger.warning("Google Calendar env token refresh failed: %s", exc)
                return None
            return token_data["access_token"], calendar_id

        return None

    @staticmethod
    def _meeting_window(db: Session, meeting: Meeting) -> tuple:
        end_at = meeting.scheduled_at + timedelta(hours=1)
        if meeting.slot_id:
            slot = (
                db.query(InterviewSlot)
                .filter(InterviewSlot.id == meeting.slot_id)
                .first()
            )
            if slot:
                end_at = slot.ends_at
        return meeting.scheduled_at, end_at

    @staticmethod
    def _event_context(db: Session, meeting: Meeting) -> dict | None:
        recruiter = (
            db.query(Recruiter).filter(Recruiter.id == meeting.recruiter_id).first()
        )
        student = db.query(Student).filter(Student.id == meeting.student_id).first()
        job = db.query(Job).filter(Job.id == meeting.job_id).first()
        if not recruiter or not student:
            return None
        start_at, end_at = MeetingCalendarSync._meeting_window(db, meeting)
        job_title = job.title if job else f"Offre #{meeting.job_id}"
        candidate_name = f"{student.first_name} {student.last_name}".strip()
        summary = f"Entretien MatiousHire — {job_title} ({candidate_name})"
        recruiter_name = f"{recruiter.first_name} {recruiter.last_name}"
        description = (
            f"Entretien de recrutement MatiousHire\n"
            f"Candidat : {candidate_name} ({student.email})\n"
            f"Recruteur : {recruiter_name} ({recruiter.email})\n"
            f"Offre : {job_title}\n"
        )
        if meeting.notes:
            description += f"\nNotes : {meeting.notes}"
        return {
            "summary": summary,
            "description": description,
            "start_at": start_at,
            "end_at": end_at,
            "location": meeting.location,
            "attendee_emails": [recruiter.email, student.email],
        }

    @staticmethod
    def _apply_event_payload(meeting: Meeting, event: dict) -> None:
        meeting.google_event_id = event.get("id")
        meeting.google_event_link = event.get("htmlLink")
        meeting.google_meet_link = extract_meet_link(event)
        meeting.updated_at = utc_now()

    @staticmethod
    def _create_event(db: Session, meeting: Meeting) -> None:
        access = MeetingCalendarSync._resolve_access(db, meeting.recruiter_id)
        context = MeetingCalendarSync._event_context(db, meeting)
        if not access or not context:
            return
        access_token, calendar_id = access
        try:
            event = GoogleCalendarService.create_event(
                access_token=access_token,
                calendar_id=calendar_id,
                with_meet=True,
                **context,
            )
            MeetingCalendarSync._apply_event_payload(meeting, event)
        except Exception as exc:
            logger.warning(
                "Google Calendar event creation failed for meeting %s: %s",
                meeting.id,
                exc,
            )

    @staticmethod
    def _update_event(db: Session, meeting: Meeting) -> None:
        access = MeetingCalendarSync._resolve_access(db, meeting.recruiter_id)
        context = MeetingCalendarSync._event_context(db, meeting)
        if not access or not context or not meeting.google_event_id:
            return
        access_token, calendar_id = access
        try:
            event = GoogleCalendarService.update_event(
                access_token=access_token,
                calendar_id=calendar_id,
                event_id=meeting.google_event_id,
                **context,
            )
            MeetingCalendarSync._apply_event_payload(meeting, event)
        except Exception as exc:
            logger.warning(
                "Google Calendar event update failed for meeting %s: %s",
                meeting.id,
                exc,
            )

    @staticmethod
    def _cancel_event(db: Session, meeting: Meeting) -> None:
        access = MeetingCalendarSync._resolve_access(db, meeting.recruiter_id)
        if not access or not meeting.google_event_id:
            return
        access_token, calendar_id = access
        try:
            GoogleCalendarService.cancel_event(
                access_token=access_token,
                calendar_id=calendar_id,
                event_id=meeting.google_event_id,
            )
        except Exception as exc:
            logger.warning(
                "Google Calendar event cancel failed for meeting %s: %s",
                meeting.id,
                exc,
            )
