"""HTTP-only cookie helpers for server-side session tokens."""

from __future__ import annotations

import os

from fastapi import Response

REFRESH_COOKIE = "matioushire_refresh"
ACCESS_COOKIE = "matioushire_access"
COOKIE_SECURE = os.getenv("AUTH_COOKIE_SECURE", "false").lower() in {"1", "true", "yes"}
COOKIE_DOMAIN = os.getenv("AUTH_COOKIE_DOMAIN") or None
USE_AUTH_COOKIES = os.getenv("AUTH_USE_COOKIES", "true").lower() in {"1", "true", "yes"}


def set_auth_cookies(
    response: Response,
    *,
    access_token: str | None = None,
    refresh_token: str | None = None,
) -> None:
    if not USE_AUTH_COOKIES:
        return
    common = {
        "httponly": True,
        "secure": COOKIE_SECURE,
        "samesite": "lax",
        "path": "/",
    }
    if COOKIE_DOMAIN:
        common["domain"] = COOKIE_DOMAIN
    if refresh_token:
        response.set_cookie(
            REFRESH_COOKIE,
            refresh_token,
            max_age=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")) * 86400,
            **common,
        )
    if access_token:
        response.set_cookie(
            ACCESS_COOKIE,
            access_token,
            max_age=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")) * 60,
            **common,
        )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(REFRESH_COOKIE, path="/")
    response.delete_cookie(ACCESS_COOKIE, path="/")
