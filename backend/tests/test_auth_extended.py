"""Tests for extended auth: refresh tokens, 2FA, OAuth providers."""

from __future__ import annotations

import pyotp

from app.modules.auth.totp_service import enable_totp, setup_totp


def test_login_returns_refresh_token(client, sample_student):
    response = client.post(
        "/auth/login",
        data={"username": sample_student.email, "password": "Password123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["role"] == "student"
    assert "matioushire_refresh" in response.cookies


def test_refresh_token_rotation(client, sample_student):
    login = client.post(
        "/auth/login",
        data={"username": sample_student.email, "password": "Password123"},
    )
    cookies = {"matioushire_refresh": login.cookies["matioushire_refresh"]}
    refreshed = client.post("/auth/refresh", cookies=cookies)
    assert refreshed.status_code == 200
    body = refreshed.json()
    assert body["access_token"]
    assert body["refresh_token"]


def test_auth_features_endpoint(client):
    response = client.get("/auth/features")
    assert response.status_code == 200
    body = response.json()
    assert body["refresh_tokens"] is True
    assert body["totp_2fa"] is True
    assert body["authorization_code_flow"] is True


def test_oauth_providers_list(client):
    response = client.get("/auth/oauth/providers")
    assert response.status_code == 200
    assert "providers" in response.json()


def test_2fa_login_flow(client, sample_student, db_session):
    secret, _uri = setup_totp(
        db_session,
        user_role="student",
        user_id=sample_student.id,
        email=sample_student.email,
    )
    enable_totp(
        db_session,
        user_role="student",
        user_id=sample_student.id,
        code=pyotp.TOTP(secret).now(),
    )
    db_session.commit()

    login = client.post(
        "/auth/login",
        data={"username": sample_student.email, "password": "Password123"},
    )
    assert login.status_code == 200
    body = login.json()
    assert body["requires_2fa"] is True
    assert body["login_challenge"]

    verify = client.post(
        "/auth/2fa/verify-login",
        json={
            "login_challenge": body["login_challenge"],
            "totp_code": pyotp.TOTP(secret).now(),
        },
    )
    assert verify.status_code == 200
    assert verify.json()["access_token"]
