"""OAuth 2.0 Authorization Code Flow — Google, GitHub, LinkedIn, OIDC."""

from __future__ import annotations

import os
import secrets
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

import httpx

from app.auth import create_oauth_state_token, decode_oauth_state_token, hash_password
from app.models.auth import OAuthAccount
from app.models.platform import Admin
from app.models.recruitment import Recruiter, Student

Role = str


@dataclass(frozen=True)
class OAuthProfile:
    provider: str
    provider_user_id: str
    email: str
    first_name: str
    last_name: str


@dataclass(frozen=True)
class OAuthProviderConfig:
    id: str
    name: str
    client_id: str
    client_secret: str
    authorize_url: str
    token_url: str
    userinfo_url: str
    scopes: list[str]
    profile_mapper: str


def _env(name: str) -> str:
    return os.getenv(name, "").strip()


def _provider_configs() -> dict[str, OAuthProviderConfig]:
    configs: dict[str, OAuthProviderConfig] = {}

    if _env("GOOGLE_CLIENT_ID") and _env("GOOGLE_CLIENT_SECRET"):
        configs["google"] = OAuthProviderConfig(
            id="google",
            name="Google",
            client_id=_env("GOOGLE_CLIENT_ID"),
            client_secret=_env("GOOGLE_CLIENT_SECRET"),
            authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
            token_url="https://oauth2.googleapis.com/token",
            userinfo_url="https://openidconnect.googleapis.com/v1/userinfo",
            scopes=["openid", "email", "profile"],
            profile_mapper="google",
        )

    if _env("GITHUB_CLIENT_ID") and _env("GITHUB_CLIENT_SECRET"):
        configs["github"] = OAuthProviderConfig(
            id="github",
            name="GitHub",
            client_id=_env("GITHUB_CLIENT_ID"),
            client_secret=_env("GITHUB_CLIENT_SECRET"),
            authorize_url="https://github.com/login/oauth/authorize",
            token_url="https://github.com/login/oauth/access_token",
            userinfo_url="https://api.github.com/user",
            scopes=["read:user", "user:email"],
            profile_mapper="github",
        )

    if _env("LINKEDIN_CLIENT_ID") and _env("LINKEDIN_CLIENT_SECRET"):
        configs["linkedin"] = OAuthProviderConfig(
            id="linkedin",
            name="LinkedIn",
            client_id=_env("LINKEDIN_CLIENT_ID"),
            client_secret=_env("LINKEDIN_CLIENT_SECRET"),
            authorize_url="https://www.linkedin.com/oauth/v2/authorization",
            token_url="https://www.linkedin.com/oauth/v2/accessToken",
            userinfo_url="https://api.linkedin.com/v2/userinfo",
            scopes=["openid", "profile", "email"],
            profile_mapper="oidc",
        )

    oidc_issuer = _env("OIDC_ISSUER").rstrip("/")
    if oidc_issuer and _env("OIDC_CLIENT_ID") and _env("OIDC_CLIENT_SECRET"):
        configs["oidc"] = OAuthProviderConfig(
            id="oidc",
            name=_env("OIDC_PROVIDER_NAME") or "Enterprise SSO (OIDC)",
            client_id=_env("OIDC_CLIENT_ID"),
            client_secret=_env("OIDC_CLIENT_SECRET"),
            authorize_url=f"{oidc_issuer}/authorize",
            token_url=f"{oidc_issuer}/oauth/token",
            userinfo_url=f"{oidc_issuer}/userinfo",
            scopes=[scope for scope in _env("OIDC_SCOPES").split() if scope]
            or ["openid", "email", "profile"],
            profile_mapper="oidc",
        )

    return configs


def list_providers() -> list[dict[str, Any]]:
    return [
        {
            "id": cfg.id,
            "name": cfg.name,
            "enabled": True,
            "authorize_path": f"/auth/oauth/{cfg.id}/authorize",
        }
        for cfg in _provider_configs().values()
    ]


def oauth_redirect_uri(provider: str) -> str:
    base = _env("OAUTH_REDIRECT_BASE") or "http://127.0.0.1:8000/auth/oauth"
    return f"{base.rstrip('/')}/{provider}/callback"


def build_authorize_url(provider: str, role: Role) -> str:
    cfg = _provider_configs().get(provider)
    if not cfg:
        raise ValueError(f"OAuth provider '{provider}' is not configured")

    state = create_oauth_state_token(provider, role)
    params = {
        "client_id": cfg.client_id,
        "redirect_uri": oauth_redirect_uri(provider),
        "response_type": "code",
        "scope": " ".join(cfg.scopes),
        "state": state,
    }
    if provider == "google":
        params["access_type"] = "online"
        params["prompt"] = "select_account"
    return f"{cfg.authorize_url}?{urlencode(params)}"


async def exchange_code(provider: str, code: str, state: str) -> OAuthProfile:
    cfg = _provider_configs().get(provider)
    if not cfg:
        raise ValueError(f"OAuth provider '{provider}' is not configured")

    decode_oauth_state_token(state, expected_provider=provider)
    redirect_uri = oauth_redirect_uri(provider)

    headers = {"Accept": "application/json"}
    data = {
        "client_id": cfg.client_id,
        "client_secret": cfg.client_secret,
        "code": code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }
    if provider == "github":
        headers["Accept"] = "application/json"

    async with httpx.AsyncClient(timeout=20.0) as client:
        token_resp = await client.post(cfg.token_url, data=data, headers=headers)
        token_resp.raise_for_status()
        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise ValueError("OAuth token exchange failed")

        user_headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        user_resp = await client.get(cfg.userinfo_url, headers=user_headers)
        user_resp.raise_for_status()
        profile_data = user_resp.json()

    if cfg.profile_mapper == "google":
        return OAuthProfile(
            provider=provider,
            provider_user_id=str(profile_data.get("sub")),
            email=profile_data.get("email", ""),
            first_name=profile_data.get("given_name") or "OAuth",
            last_name=profile_data.get("family_name") or "User",
        )

    if cfg.profile_mapper == "github":
        email = profile_data.get("email")
        if not email:
            async with httpx.AsyncClient(timeout=20.0) as client:
                emails_resp = await client.get(
                    "https://api.github.com/user/emails",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/json",
                    },
                )
                emails_resp.raise_for_status()
                emails = emails_resp.json()
                primary = next(
                    (item for item in emails if item.get("primary")),
                    emails[0] if emails else None,
                )
                email = primary.get("email") if primary else ""
        display_name = (
            profile_data.get("name") or profile_data.get("login") or "OAuth User"
        )
        name = display_name.split(" ", 1)
        first = name[0]
        last = name[1] if len(name) > 1 else "User"
        return OAuthProfile(
            provider=provider,
            provider_user_id=str(profile_data.get("id")),
            email=email or "",
            first_name=first,
            last_name=last,
        )

    return OAuthProfile(
        provider=provider,
        provider_user_id=str(profile_data.get("sub") or profile_data.get("id")),
        email=profile_data.get("email", ""),
        first_name=(
            profile_data.get("given_name") or profile_data.get("name") or "OAuth"
        ),
        last_name=profile_data.get("family_name") or "User",
    )


def _random_password() -> str:
    return secrets.token_urlsafe(32)


def resolve_oauth_user(db, profile: OAuthProfile, role: Role):
    if not profile.email:
        raise ValueError("OAuth provider did not return an email address")

    linked = (
        db.query(OAuthAccount)
        .filter(
            OAuthAccount.provider == profile.provider,
            OAuthAccount.provider_user_id == profile.provider_user_id,
        )
        .first()
    )
    if linked:
        return linked.email, linked.role, linked.user_id

    if role in {"student", "candidate"}:
        user = db.query(Student).filter(Student.email == profile.email).first()
        if not user:
            user = Student(
                email=profile.email,
                hashed_password=hash_password(_random_password()),
                first_name=profile.first_name,
                last_name=profile.last_name,
                account_kind=role,
            )
            db.add(user)
            db.flush()
        user_table = "students"
        user_id = user.id
    elif role == "recruiter":
        user = db.query(Recruiter).filter(Recruiter.email == profile.email).first()
        if not user:
            user = Recruiter(
                email=profile.email,
                hashed_password=hash_password(_random_password()),
                first_name=profile.first_name,
                last_name=profile.last_name,
                company_name=f"{profile.first_name} Company",
            )
            db.add(user)
            db.flush()
        user_table = "recruiters"
        user_id = user.id
    elif role == "admin":
        user = db.query(Admin).filter(Admin.email == profile.email).first()
        if not user:
            raise ValueError(
                "Admin OAuth login requires a pre-provisioned admin account"
            )
        user_table = "admins"
        user_id = user.id
    else:
        raise ValueError("Unsupported role for OAuth login")

    db.add(
        OAuthAccount(
            provider=profile.provider,
            provider_user_id=profile.provider_user_id,
            email=profile.email,
            role=role,
            user_table=user_table,
            user_id=user_id,
        )
    )
    db.flush()
    return profile.email, role, user_id
