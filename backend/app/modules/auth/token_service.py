"""Refresh token persistence and rotation."""

from __future__ import annotations

import hashlib
import os
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.auth import create_access_token, create_refresh_token, decode_token
from app.models.auth import RefreshToken
from app.schemas.auth_extended import TokenPairOut

REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def issue_token_pair(db: Session, *, email: str, role: str) -> TokenPairOut:
    access_token = create_access_token(email, role)  # type: ignore[arg-type]
    refresh_token = create_refresh_token(email, role)  # type: ignore[arg-type]
    expires_at = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    db.add(
        RefreshToken(
            token_hash=_hash_token(refresh_token),
            subject_email=email,
            role=role,
            expires_at=expires_at.replace(tzinfo=None),
        )
    )
    db.flush()
    return TokenPairOut(
        access_token=access_token,
        refresh_token=refresh_token,
        role=role,
    )


def refresh_tokens(db: Session, raw_refresh: str) -> TokenPairOut:
    decode_token(raw_refresh, expected_type="refresh")
    token_hash = _hash_token(raw_refresh)
    stored = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked.is_(False),
        )
        .first()
    )
    if not stored:
        raise ValueError("Invalid refresh token")
    if stored.expires_at.replace(tzinfo=UTC) < datetime.now(UTC):
        stored.revoked = True
        db.flush()
        raise ValueError("Refresh token expired")

    stored.revoked = True
    db.flush()
    return issue_token_pair(db, email=stored.subject_email, role=stored.role)


def revoke_refresh_token(db: Session, raw_refresh: str) -> None:
    token_hash = _hash_token(raw_refresh)
    stored = (
        db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    )
    if stored:
        stored.revoked = True
        db.flush()
