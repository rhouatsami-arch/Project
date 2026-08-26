"""Google Calendar integration for meetings."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import patch

import pytest

from app.models.platform import GoogleCalendarConnection, Meeting
from app.models.recruitment import Application, ApplicationStatus
from app.modules.platform.meeting_calendar_sync import MeetingCalendarSync


@pytest.fixture()
def auth_headers_recruiter(client, sample_recruiter) -> dict[str, str]:
    response = client.post(
        "/auth/login",
        data={"username": sample_recruiter.email, "password": "Password123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def meeting_setup(db_session, sample_recruiter, sample_student, sample_job):
    application = Application(
        student_id=sample_student.id,
        job_id=sample_job.id,
        status=ApplicationStatus.interview_invited,
    )
    db_session.add(application)
    db_session.commit()
    db_session.refresh(application)
    meeting = Meeting(
        application_id=application.id,
        recruiter_id=sample_recruiter.id,
        student_id=sample_student.id,
        job_id=sample_job.id,
        scheduled_at=application.created_at + timedelta(days=2),
        location="Visio",
        notes="Test interview",
        status="accepted",
    )
    db_session.add(meeting)
    db_session.commit()
    db_session.refresh(meeting)
    return meeting


def test_google_calendar_status_not_connected(client, auth_headers_recruiter):
    with patch(
        "app.routers.meetings.is_calendar_configured",
        return_value=True,
    ):
        response = client.get("/meetings/google/status", headers=auth_headers_recruiter)
    assert response.status_code == 200
    body = response.json()
    assert body["configured"] is True
    assert body["connected"] is False


def test_google_calendar_authorize_url(client, auth_headers_recruiter):
    with (
        patch(
            "app.routers.meetings.is_calendar_configured",
            return_value=True,
        ),
        patch(
            "app.routers.meetings.GoogleCalendarService.build_authorize_url",
            return_value="https://accounts.google.com/o/oauth2/v2/auth?test=1",
        ),
    ):
        response = client.get(
            "/meetings/google/authorize",
            headers=auth_headers_recruiter,
        )
    assert response.status_code == 200
    assert "authorization_url" in response.json()


def test_sync_on_accepted_creates_event(db_session, sample_recruiter, meeting_setup):
    db_session.add(
        GoogleCalendarConnection(
            recruiter_id=sample_recruiter.id,
            refresh_token="refresh-test",
            access_token="access-test",
        )
    )
    db_session.commit()

    fake_event = {
        "id": "evt_123",
        "htmlLink": "https://calendar.google.com/event?eid=123",
        "conferenceData": {
            "entryPoints": [
                {
                    "entryPointType": "video",
                    "uri": "https://meet.google.com/abc-defg-hij",
                }
            ],
        },
    }

    with (
        patch(
            "app.modules.platform.meeting_calendar_sync.is_calendar_configured",
            return_value=True,
        ),
        patch(
            "app.modules.platform.meeting_calendar_sync.GoogleCalendarService.refresh_access_token",
            return_value={"access_token": "access-test", "expires_in": 3600},
        ),
        patch(
            "app.modules.platform.meeting_calendar_sync.GoogleCalendarService.create_event",
            return_value=fake_event,
        ) as create_mock,
    ):
        MeetingCalendarSync.sync_on_accepted(db_session, meeting_setup)

    create_mock.assert_called_once()
    assert meeting_setup.google_event_id == "evt_123"
    assert (
        meeting_setup.google_event_link == "https://calendar.google.com/event?eid=123"
    )
    assert meeting_setup.google_meet_link == "https://meet.google.com/abc-defg-hij"


def test_confirm_meeting_triggers_calendar_sync(
    client,
    db_session,
    sample_student,
    sample_recruiter,
    meeting_setup,
    auth_headers_student,
):
    meeting_setup.status = "proposed"
    db_session.commit()

    db_session.add(
        GoogleCalendarConnection(
            recruiter_id=sample_recruiter.id,
            refresh_token="refresh-test",
            access_token="access-test",
        )
    )
    db_session.commit()

    fake_event = {
        "id": "evt_confirm",
        "htmlLink": "https://calendar.google.com/event?eid=confirm",
        "hangoutLink": "https://meet.google.com/xyz",
    }

    with (
        patch(
            "app.modules.platform.meeting_calendar_sync.is_calendar_configured",
            return_value=True,
        ),
        patch(
            "app.modules.platform.meeting_calendar_sync.GoogleCalendarService.refresh_access_token",
            return_value={"access_token": "access-test", "expires_in": 3600},
        ),
        patch(
            "app.modules.platform.meeting_calendar_sync.GoogleCalendarService.create_event",
            return_value=fake_event,
        ),
    ):
        response = client.post(
            f"/meetings/students/{meeting_setup.id}/confirm",
            headers=auth_headers_student,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "accepted"
    assert body["google_event_link"] == "https://calendar.google.com/event?eid=confirm"
    assert body["google_meet_link"] == "https://meet.google.com/xyz"
