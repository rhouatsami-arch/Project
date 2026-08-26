-- Add auth / calendar tables missing from older databases (safe to re-run)

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    token_hash VARCHAR(128) UNIQUE NOT NULL,
    subject_email VARCHAR(255) NOT NULL,
    role VARCHAR(30) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_refresh_tokens_subject_email ON refresh_tokens (subject_email);

CREATE TABLE IF NOT EXISTS oauth_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider VARCHAR(30) NOT NULL,
    provider_user_id VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(30) NOT NULL,
    user_table VARCHAR(30) NOT NULL,
    user_id UUID NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (provider, provider_user_id)
);

CREATE TABLE IF NOT EXISTS mfa_secrets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    user_role VARCHAR(30) NOT NULL,
    user_id UUID NOT NULL,
    totp_secret VARCHAR(64) NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    backup_codes_hash TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS google_calendar_connections (
    recruiter_id UUID PRIMARY KEY REFERENCES recruiters(id) ON DELETE CASCADE,
    google_email VARCHAR(255),
    refresh_token TEXT NOT NULL,
    access_token TEXT,
    token_expires_at TIMESTAMP,
    calendar_id VARCHAR(255) NOT NULL DEFAULT 'primary',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP
);

ALTER TABLE meetings ADD COLUMN IF NOT EXISTS google_event_id VARCHAR(255);
ALTER TABLE meetings ADD COLUMN IF NOT EXISTS google_event_link VARCHAR(512);
ALTER TABLE meetings ADD COLUMN IF NOT EXISTS google_meet_link VARCHAR(512);
