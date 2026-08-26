"""TOTP-based two-factor authentication (MFA)."""

from __future__ import annotations

import json
import secrets
from uuid import UUID

import pyotp
from sqlalchemy.orm import Session

from app.auth import hash_password, verify_password
from app.models.auth import MfaSecret

ISSUER = "MatiousHire"


def setup_totp(
    db: Session,
    *,
    user_role: str,
    user_id: UUID,
    email: str,
) -> tuple[str, str]:
    secret = pyotp.random_base32()
    existing = db.query(MfaSecret).filter(MfaSecret.email == email).first()
    if existing:
        existing.totp_secret = secret
        existing.enabled = False
        existing.user_role = user_role
        existing.user_id = user_id
    else:
        db.add(
            MfaSecret(
                email=email,
                user_role=user_role,
                user_id=user_id,
                totp_secret=secret,
                enabled=False,
            )
        )
    db.flush()
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=ISSUER)
    return secret, uri


def enable_totp(
    db: Session,
    *,
    user_role: str,
    user_id: UUID,
    code: str,
) -> bool:
    record = (
        db.query(MfaSecret)
        .filter(MfaSecret.user_role == user_role, MfaSecret.user_id == user_id)
        .first()
    )
    if not record:
        raise ValueError("2FA setup not started")
    totp = pyotp.TOTP(record.totp_secret)
    if not totp.verify(code, valid_window=1):
        raise ValueError("Invalid TOTP code")
    backup_codes = [secrets.token_hex(4) for _ in range(8)]
    hashed_codes = [hash_password(code) for code in backup_codes]
    record.backup_codes_hash = json.dumps(hashed_codes)
    record.enabled = True
    db.flush()
    return True


def is_mfa_enabled(db: Session, email: str) -> bool:
    record = (
        db.query(MfaSecret).filter(MfaSecret.email == email, MfaSecret.enabled).first()
    )
    return record is not None


def verify_totp(db: Session, email: str, code: str) -> bool:
    record = (
        db.query(MfaSecret).filter(MfaSecret.email == email, MfaSecret.enabled).first()
    )
    if not record:
        return False
    if pyotp.TOTP(record.totp_secret).verify(code, valid_window=1):
        return True
    if record.backup_codes_hash:
        hashes = json.loads(record.backup_codes_hash)
        for index, hashed in enumerate(hashes):
            if verify_password(code, hashed):
                hashes.pop(index)
                record.backup_codes_hash = json.dumps(hashes) if hashes else None
                db.flush()
                return True
    return False
