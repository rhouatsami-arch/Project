from pydantic import BaseModel, Field


class TokenPairOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str


class LoginResponse(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "bearer"
    role: str | None = None
    requires_2fa: bool = False
    login_challenge: str | None = None


class RefreshRequest(BaseModel):
    refresh_token: str | None = None


class AuthFeaturesOut(BaseModel):
    refresh_tokens: bool = True
    totp_2fa: bool = True
    authorization_code_flow: bool = True
    oauth_social: bool = True
    server_session_cookies: bool = True
    oidc_enterprise_sso: bool = True
    saml_sso: bool = False
    saml_note: str = (
        "Enterprise SAML IdPs (Okta, Azure AD) are supported via OIDC bridge "
        "or dedicated SAML integration."
    )


class OAuthProviderOut(BaseModel):
    id: str
    name: str
    enabled: bool
    authorize_path: str


class OAuthProvidersOut(BaseModel):
    providers: list[OAuthProviderOut]


class MfaSetupOut(BaseModel):
    secret: str
    provisioning_uri: str
    issuer: str = "MatiousHire"


class MfaEnableRequest(BaseModel):
    totp_code: str = Field(min_length=6, max_length=6)


class MfaVerifyLoginRequest(BaseModel):
    login_challenge: str
    totp_code: str = Field(min_length=6, max_length=6)
