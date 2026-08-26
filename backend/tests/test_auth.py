"""Unit tests for authentication helpers."""

import pytest
from fastapi import HTTPException

from app.auth import create_access_token, decode_token, hash_password, verify_password


def test_hash_and_verify_password_roundtrip():
    hashed = hash_password("Secret123!")
    assert verify_password("Secret123!", hashed)
    assert not verify_password("wrong", hashed)


def test_create_and_decode_access_token():
    token = create_access_token("user@test.com", "student")
    payload = decode_token(token)
    assert payload["sub"] == "user@test.com"
    assert payload["role"] == "student"


def test_decode_token_rejects_tampered_signature():
    token = create_access_token("user@test.com", "student")
    body, _signature = token.rsplit(".", 1)
    tampered = f"{body}.invalidsignature"

    with pytest.raises(HTTPException) as exc_info:
        decode_token(tampered)
    assert exc_info.value.status_code == 401
