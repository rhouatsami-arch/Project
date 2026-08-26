-- MatiousHire bootstrap schema (PostgreSQL)
-- Note: the FastAPI app stores student/candidate profiles in `students`
-- with account_kind = 'student' | 'candidate'. The `candidates` table
-- mirrors candidate accounts for SQL/bootstrap scripts and legacy migration 0005.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

DROP TABLE IF EXISTS
    audit_logs,
    mfa_secrets,
    oauth_accounts,
    refresh_tokens,
    recommendation_history,
    notifications,
    google_calendar_connections,
    meetings,
    candidate_availabilities,
    interview_slots,
    saved_jobs,
    applications,
    jobs,
    candidates,
    recruiters,
    students,
    admins
CASCADE;

DROP TYPE IF EXISTS notificationtype;
DROP TYPE IF EXISTS meetingstatus;
DROP TYPE IF EXISTS internshipdurationtype;
DROP TYPE IF EXISTS applicationstatus;
DROP TYPE IF EXISTS jobstatus;

CREATE TYPE jobstatus AS ENUM ('open', 'closed');
CREATE TYPE applicationstatus AS ENUM (
    'applied',
    'shortlisted',
    'interview_invited',
    'rejected',
    'hired'
);
CREATE TYPE internshipdurationtype AS ENUM (
    'observation',
    'operational',
    'functional'
);
CREATE TYPE meetingstatus AS ENUM (
    'proposed',
    'accepted',
    'refused',
    'completed',
    'cancelled'
);
CREATE TYPE notificationtype AS ENUM ('recommendation', 'interview', 'system');

CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(30),
    university VARCHAR(255),
    field_of_study VARCHAR(255),
    graduation_year INT,
    bio TEXT,
    skills TEXT,
    technical_skills TEXT,
    soft_skills TEXT,
    experiences TEXT,
    projects TEXT,
    certifications TEXT,
    languages TEXT,
    internship_type VARCHAR(255),
    internship_duration VARCHAR(255),
    account_kind VARCHAR(30) NOT NULL DEFAULT 'student',
    cv_filename VARCHAR(255),
    cv_path VARCHAR(500),
    cv_extracted_text TEXT,
    cv_extracted_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_students_email ON students (email);
CREATE INDEX ix_students_account_kind ON students (account_kind);

CREATE TABLE candidates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(30),
    university VARCHAR(255),
    field_of_study VARCHAR(255),
    graduation_year INT,
    bio TEXT,
    skills TEXT,
    technical_skills TEXT,
    soft_skills TEXT,
    experiences TEXT,
    projects TEXT,
    certifications TEXT,
    languages TEXT,
    cv_filename VARCHAR(255),
    cv_path VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_candidates_email ON candidates (email);

CREATE TABLE recruiters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    phone VARCHAR(30),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_recruiters_email ON recruiters (email);

CREATE TABLE admins (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_admins_email ON admins (email);

CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    recruiter_id UUID NOT NULL REFERENCES recruiters(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    required_skills TEXT,
    location VARCHAR(255),
    employment_type VARCHAR(50) DEFAULT 'full_time',
    status jobstatus NOT NULL DEFAULT 'open',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    job_id INT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    cover_letter TEXT,
    internship_type internshipdurationtype,
    status applicationstatus NOT NULL DEFAULT 'applied',
    match_score INT NOT NULL DEFAULT 0,
    interview_message TEXT,
    interview_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_student_job_application UNIQUE (student_id, job_id)
);

CREATE TABLE saved_jobs (
    id SERIAL PRIMARY KEY,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    job_id INT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_student_saved_job UNIQUE (student_id, job_id)
);

CREATE TABLE interview_slots (
    id SERIAL PRIMARY KEY,
    recruiter_id UUID NOT NULL REFERENCES recruiters(id) ON DELETE CASCADE,
    starts_at TIMESTAMP NOT NULL,
    ends_at TIMESTAMP NOT NULL,
    is_booked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_interview_slots_recruiter_id ON interview_slots (recruiter_id);

CREATE TABLE candidate_availabilities (
    id SERIAL PRIMARY KEY,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    starts_at TIMESTAMP NOT NULL,
    ends_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_candidate_availabilities_student_id
    ON candidate_availabilities (student_id);

CREATE TABLE meetings (
    id SERIAL PRIMARY KEY,
    application_id INT NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    recruiter_id UUID NOT NULL REFERENCES recruiters(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    job_id INT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    slot_id INT REFERENCES interview_slots(id) ON DELETE SET NULL,
    scheduled_at TIMESTAMP NOT NULL,
    location VARCHAR(255),
    notes TEXT,
    status meetingstatus NOT NULL DEFAULT 'proposed',
    google_event_id VARCHAR(255),
    google_event_link VARCHAR(512),
    google_meet_link VARCHAR(512),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP
);

CREATE TABLE google_calendar_connections (
    recruiter_id UUID PRIMARY KEY REFERENCES recruiters(id) ON DELETE CASCADE,
    google_email VARCHAR(255),
    refresh_token TEXT NOT NULL,
    access_token TEXT,
    token_expires_at TIMESTAMP,
    calendar_id VARCHAR(255) NOT NULL DEFAULT 'primary',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP
);

CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    user_role VARCHAR(30) NOT NULL,
    type notificationtype NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_notifications_user_email ON notifications (user_email);

CREATE TABLE recommendation_history (
    id SERIAL PRIMARY KEY,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    job_id INT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    compatibility_score INT NOT NULL DEFAULT 0,
    explanation TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    token_hash VARCHAR(128) UNIQUE NOT NULL,
    subject_email VARCHAR(255) NOT NULL,
    role VARCHAR(30) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE oauth_accounts (
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

CREATE TABLE mfa_secrets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    user_role VARCHAR(30) NOT NULL,
    user_id UUID NOT NULL,
    totp_secret VARCHAR(64) NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    backup_codes_hash TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    actor_email VARCHAR(255) NOT NULL,
    actor_role VARCHAR(30) NOT NULL,
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(255),
    details TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
