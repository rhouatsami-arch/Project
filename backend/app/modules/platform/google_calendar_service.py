"""Google Calendar OAuth + REST API (events with optional Google Meet)."""

from __future__ import annotations

import logging
import os
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlencode

import httpx

logger = logging.getLogger(__name__)

CALENDAR_SCOPE = "https://www.googleapis.com/auth/calendar.events"
CALENDAR_API_BASE = "https://www.googleapis.com/calendar/v3"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


def _env(name: str) -> str:
    return os.getenv(name, "").strip()


def calendar_client_id() -> str:
    return _env("GOOGLE_CALENDAR_CLIENT_ID") or _env("GOOGLE_CLIENT_ID")


def calendar_client_secret() -> str:
    return _env("GOOGLE_CALENDAR_CLIENT_SECRET") or _env("GOOGLE_CLIENT_SECRET")


def calendar_redirect_uri() -> str:
    explicit = _env("GOOGLE_CALENDAR_REDIRECT_URI")
    if explicit:
        return explicit
    api_base = _env("API_PUBLIC_URL") or "http://127.0.0.1:8000"
    return f"{api_base.rstrip('/')}/meetings/google/callback"


def calendar_frontend_redirect() -> str:
    oauth_callback = _env("FRONTEND_OAUTH_CALLBACK")
    meetings_redirect = (
        oauth_callback.replace("/login/oauth/callback", "/recruiter/meetings")
        if oauth_callback
        else None
    )
    return (
        _env("GOOGLE_CALENDAR_FRONTEND_REDIRECT")
        or meetings_redirect
        or "http://127.0.0.1:3000/recruiter/meetings"
    )


def is_calendar_configured() -> bool:
    return bool(calendar_client_id() and calendar_client_secret())


class GoogleCalendarService:
    @staticmethod
    def build_authorize_url(state: str) -> str:
        params = {
            "client_id": calendar_client_id(),
            "redirect_uri": calendar_redirect_uri(),
            "response_type": "code",
            "scope": CALENDAR_SCOPE,
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
        return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    @staticmethod
    def exchange_code(code: str) -> dict[str, Any]:
        response = httpx.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": calendar_client_id(),
                "client_secret": calendar_client_secret(),
                "redirect_uri": calendar_redirect_uri(),
                "grant_type": "authorization_code",
            },
            timeout=20.0,
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def refresh_access_token(refresh_token: str) -> dict[str, Any]:
        response = httpx.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": calendar_client_id(),
                "client_secret": calendar_client_secret(),
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=20.0,
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _auth_headers(access_token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {access_token}"}

    @staticmethod
    def create_event(
        *,
        access_token: str,
        calendar_id: str,
        summary: str,
        description: str,
        start_at: datetime,
        end_at: datetime,
        location: str | None,
        attendee_emails: list[str],
        with_meet: bool = True,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": _to_rfc3339(start_at), "timeZone": "UTC"},
            "end": {"dateTime": _to_rfc3339(end_at), "timeZone": "UTC"},
            "attendees": [{"email": email} for email in attendee_emails if email],
            "reminders": {"useDefault": True},
        }
        if location:
            body["location"] = location
        params: dict[str, str] = {}
        if with_meet:
            body["conferenceData"] = {
                "createRequest": {
                    "requestId": secrets.token_hex(8),
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            }
            params["conferenceDataVersion"] = "1"
        response = httpx.post(
            f"{CALENDAR_API_BASE}/calendars/{calendar_id}/events",
            headers=GoogleCalendarService._auth_headers(access_token),
            params=params,
            json=body,
            timeout=20.0,
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def update_event(
        *,
        access_token: str,
        calendar_id: str,
        event_id: str,
        summary: str,
        description: str,
        start_at: datetime,
        end_at: datetime,
        location: str | None,
        attendee_emails: list[str],
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": _to_rfc3339(start_at), "timeZone": "UTC"},
            "end": {"dateTime": _to_rfc3339(end_at), "timeZone": "UTC"},
            "attendees": [{"email": email} for email in attendee_emails if email],
        }
        if location:
            body["location"] = location
        response = httpx.patch(
            f"{CALENDAR_API_BASE}/calendars/{calendar_id}/events/{event_id}",
            headers=GoogleCalendarService._auth_headers(access_token),
            json=body,
            timeout=20.0,
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def cancel_event(
        *,
        access_token: str,
        calendar_id: str,
        event_id: str,
    ) -> None:
        response = httpx.delete(
            f"{CALENDAR_API_BASE}/calendars/{calendar_id}/events/{event_id}",
            headers=GoogleCalendarService._auth_headers(access_token),
            timeout=20.0,
        )
        if response.status_code not in {204, 410}:
            response.raise_for_status()

    @staticmethod
    def fetch_user_email(access_token: str) -> str | None:
        try:
            response = httpx.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers=GoogleCalendarService._auth_headers(access_token),
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json().get("email")
        except httpx.HTTPError:
            logger.warning(
                "Could not fetch Google account email for calendar connection"
            )
            return None


def _to_rfc3339(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    else:
        value = value.astimezone(UTC)
    return value.isoformat().replace("+00:00", "Z")


def token_expires_at(expires_in: int | None) -> datetime | None:
    if not expires_in:
        return None
    return datetime.now(UTC).replace(tzinfo=None) + timedelta(seconds=int(expires_in))


def extract_meet_link(event: dict[str, Any]) -> str | None:
    for entry in event.get("conferenceData", {}).get("entryPoints", []):
        if entry.get("entryPointType") == "video":
            return entry.get("uri")
    return event.get("hangoutLink")
