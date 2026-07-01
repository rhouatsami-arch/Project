CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

DROP TABLE IF EXISTS activity_events, chat_messages, chat_sessions,
skill_quizzes, quiz_attempts, quiz_questions, quizzes,
candidate_cv_shares, candidate_ratings, recommendations,
interview_slots, student_recruiter_meetings, recruiter_interviews,
interviews, candidate_documents, candidate_favorites,
candidate_job_applications, applications, jobs, experiences,
candidate_experiences, candidate_cvs, candidates, admins,
recruiters, students CASCADE;

CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    university VARCHAR(255),
    field_of_study VARCHAR(255),
    graduation_year INT,
    skills TEXT, bio TEXT,
    cv_url VARCHAR(500),
    linkedin_url VARCHAR(500),
    github_url VARCHAR(500),
    is_visible BOOLEAN DEFAULT TRUE,
    role VARCHAR(20) DEFAULT 'student',
    internship_duration_months INT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE recruiters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    industry VARCHAR(255),
    job_title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE admins (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_superadmin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE candidates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    headline VARCHAR(255),
    phone VARCHAR(20),
    bio TEXT, skills TEXT,
    location VARCHAR(255),
    linkedin_url VARCHAR(500),
    github_url VARCHAR(500),
    cv_url VARCHAR(500),
    is_visible BOOLEAN DEFAULT TRUE,
    status VARCHAR(20) DEFAULT 'active',
    student_id UUID REFERENCES students(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE candidate_cvs (
    id SERIAL PRIMARY KEY,
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INT,
    uploaded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE candidate_experiences (
    id SERIAL PRIMARY KEY,
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    role_title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    start_year INT, end_year INT,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE experiences (
    id SERIAL PRIMARY KEY,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    type VARCHAR(50) DEFAULT 'full_time',
    description TEXT, skills_used TEXT,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    is_current BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    recruiter_id UUID NOT NULL REFERENCES recruiters(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT,
    location VARCHAR(255),
    type VARCHAR(20) DEFAULT 'full_time',
    status VARCHAR(20) DEFAULT 'open',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    job_id INT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending',
    cover_letter TEXT,
    ats_score INT, ai_match_score INT,
    applied_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(student_id, job_id)
);

CREATE TABLE candidate_job_applications (
    id SERIAL PRIMARY KEY,
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    job_id INT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending',
    cover_note TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE candidate_favorites (
    id SERIAL PRIMARY KEY,
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    job_id INT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    saved_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE candidate_documents (
    id SERIAL PRIMARY KEY,
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE interviews (
    id SERIAL PRIMARY KEY,
    application_id INT REFERENCES applications(id) ON DELETE SET NULL,
    scheduled_by_recruiter_id UUID NOT NULL REFERENCES recruiters(id) ON DELETE CASCADE,
    student_id UUID REFERENCES students(id) ON DELETE SET NULL,
    starts_at TIMESTAMP NOT NULL,
    duration_minutes INT DEFAULT 30,
    meeting_link VARCHAR(500),
    meeting_type VARCHAR(50) DEFAULT 'video',
    location VARCHAR(255),
    notes TEXT,
    status VARCHAR(20) DEFAULT 'scheduled',
    outcome VARCHAR(50),
    feedback_submitted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE recruiter_interviews (
    id SERIAL PRIMARY KEY,
    recruiter_id UUID NOT NULL REFERENCES recruiters(id) ON DELETE CASCADE,
    student_id UUID REFERENCES students(id) ON DELETE SET NULL,
    job_title VARCHAR(255),
    scheduled_at TIMESTAMP NOT NULL,
    duration_min INT DEFAULT 30,
    meeting_link VARCHAR(500),
    notes TEXT,
    status VARCHAR(20) DEFAULT 'scheduled',
    ats_score INT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE student_recruiter_meetings (
    id SERIAL PRIMARY KEY,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    recruiter_id UUID NOT NULL REFERENCES recruiters(id) ON DELETE CASCADE,
    starts_at TIMESTAMP NOT NULL,
    duration_minutes INT DEFAULT 30,
    status VARCHAR(20) DEFAULT 'scheduled',
    meeting_type VARCHAR(50) DEFAULT 'video',
    location VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE interview_slots (
    id SERIAL PRIMARY KEY,
    recruiter_id UUID NOT NULL REFERENCES recruiters(id) ON DELETE CASCADE,
    job_id INT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    application_id INT REFERENCES applications(id) ON DELETE SET NULL,
    student_id UUID REFERENCES students(id) ON DELETE SET NULL,
    scheduled_at TIMESTAMP NOT NULL,
    duration_min INT DEFAULT 30,
    meeting_link VARCHAR(500),
    status VARCHAR(20) DEFAULT 'available',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    job_id INT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    match_score INT, reasons TEXT,
    generated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE candidate_ratings (
    id SERIAL PRIMARY KEY,
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    recruiter_id UUID NOT NULL REFERENCES recruiters(id) ON DELETE CASCADE,
    stars INT CHECK (stars BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE candidate_cv_shares (
    id SERIAL PRIMARY KEY,
    candidate_id UUID NOT NULL REFERENCES candidates(id) ON DELETE CASCADE,
    recruiter_id UUID NOT NULL REFERENCES recruiters(id) ON DELETE CASCADE,
    job_id INT REFERENCES jobs(id) ON DELETE SET NULL,
    message TEXT,
    sent_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE quizzes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT, topic VARCHAR(100),
    difficulty VARCHAR(20) DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE quiz_questions (
    id SERIAL PRIMARY KEY,
    quiz_id INT NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    option_a VARCHAR(500), option_b VARCHAR(500),
    option_c VARCHAR(500), option_d VARCHAR(500),
    correct_answer VARCHAR(1) NOT NULL,
    explanation TEXT
);

CREATE TABLE quiz_attempts (
    id SERIAL PRIMARY KEY,
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    quiz_id INT NOT NULL REFERENCES quizzes(id) ON DELETE CASCADE,
    score INT DEFAULT 0, total INT DEFAULT 0,
    passed BOOLEAN DEFAULT FALSE,
    attempted_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE skill_quizzes (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT, category VARCHAR(100),
    duration_minutes INT DEFAULT 30,
    questions_json TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE chat_sessions (
    id SERIAL PRIMARY KEY,
    session_key VARCHAR(100) UNIQUE NOT NULL,
    student_id INT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INT NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE activity_events (
    id SERIAL PRIMARY KEY,
    recruiter_id UUID REFERENCES recruiters(id) ON DELETE SET NULL,
    student_id UUID REFERENCES students(id) ON DELETE SET NULL,
    event_type VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id UUID,
    event_metadata TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_students_email       ON students(email);
CREATE INDEX idx_recruiters_email     ON recruiters(email);
CREATE INDEX idx_candidates_email     ON candidates(email);
CREATE INDEX idx_jobs_recruiter       ON jobs(recruiter_id);
CREATE INDEX idx_jobs_status          ON jobs(status, is_active);
CREATE INDEX idx_applications_student ON applications(student_id);
CREATE INDEX idx_applications_job     ON applications(job_id);
CREATE INDEX idx_applications_status  ON applications(status);
CREATE INDEX idx_experiences_student  ON experiences(student_id);
CREATE INDEX idx_interviews_recruiter ON recruiter_interviews(recruiter_id);
CREATE INDEX idx_activity_date        ON activity_events(created_at);
