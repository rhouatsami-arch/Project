# MatiousHire — Official PFE Documentation

**Projet de Fin d’Études — 2026**  
Intelligent HR & Recruitment Platform

This document is the **canonical academic booklet** for jury evaluation.  
It supersedes the condensed 7-page PDF export and aligns with the implemented codebase.

| Service | URL |
|---------|-----|
| Frontend | http://127.0.0.1:3000 |
| Backend API | http://127.0.0.1:8000 |
| OpenAPI (Swagger) | http://127.0.0.1:8000/docs |
| LLM module metadata | http://127.0.0.1:8000/llm/module |

**API version:** 1.4.0 · **Approach:** hybrid grounded NLP + explainable LLM

---

## Table of contents

1. [Problem statement](#1-problem-statement)
2. [Objectives and contributions](#2-objectives-and-contributions)
3. [Key capabilities](#3-key-capabilities)
4. [System architecture](#4-system-architecture)
5. [Technology stack](#5-technology-stack)
6. [Repository structure](#6-repository-structure)
7. [AI matching engine](#7-ai-matching-engine)
8. [Explainable LLM and HallucinationGuard](#8-explainable-llm-and-hallucinationguard)
9. [Security model](#9-security-model)
10. [API domain architecture](#10-api-domain-architecture)
11. [User roles and frontend routes](#11-user-roles-and-frontend-routes)
12. [Installation and quick start](#12-installation-and-quick-start)
13. [Quality assurance](#13-quality-assurance)
14. [Jury demo protocol](#14-jury-demo-protocol)
15. [Academic notice](#15-academic-notice)

---

## 1. Problem statement

Recruiters receive large volumes of unstructured CVs. Manual screening is **slow**, **subjective**, and **poorly documented**. Candidates and students cannot see *why* an offer matches (or does not match) their profile.

**MatiousHire** automates CV–job compatibility with a **transparent NLP score**, then converts that score into a **human-readable explanation**. Unlike a black-box generative LLM, the system **does not invent qualifications**. Every claim is checked against the CV, the job, and the numeric breakdown.

**Design principles**

| Principle | Meaning in this project |
|-----------|-------------------------|
| Explainable AI | Each global score is decomposed into six sub-metrics |
| Human-in-the-loop | AI assists ranking; the recruiter decides |
| Modular domain | HTTP routers ≠ scoring formulas ≠ LLM templates |
| Grounded generation | Text is produced from structured evidence only |
| Production foundations | JWT rotation, RBAC, audit logs, schema migrations |

---

## 2. Objectives and contributions

| Objective | Deliverable in the codebase |
|-----------|-----------------------------|
| End-to-end recruitment workflow | Auth, profiles, CV upload, jobs, applications, interviews |
| Intelligent matching | 6-stage NLP pipeline + weighted formula |
| Explainable AI | Template LLM + `HallucinationGuard` |
| Recruiter decision support | Ranked pipeline, score breakdown, missing skills |
| Traceability | `grounded_sources`, `confidence_score`, audit logs |

**What MatiousHire is not:** an OpenAI/GPT wrapper. The “LLM” module is a **hybrid explainable engine** (`app/modules/llm/`) that verbalizes matching scores.

---

## 3. Key capabilities

### Student / Candidate
- Registration, profile, CV upload (PDF, DOCX, TXT) and text extraction
- Job discovery, applications, saved jobs
- Personalized recommendations
- Compatibility explanation (score, strengths, missing skills)
- Interview availability, confirm / refuse / reschedule

### Recruiter
- Job lifecycle (create, update, close)
- Candidate pipeline with filters (minimum score, status, search)
- Ranked list with multi-criteria breakdown
- Per-application AI explanation drawer
- Actions: shortlist, reject, hire, invite
- Interview scheduling with optional **Google Calendar** sync

### Administrator
- Platform dashboard
- User administration (students, candidates, recruiters)
- Security and audit-log inspection

---

## 4. System architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    Presentation layer                            │
│              Next.js 15 · React 19 · TypeScript                  │
│   /login · /student/* · /candidate/* · /recruiter/* · /admin/*   │
└────────────────────────────┬─────────────────────────────────────┘
                             │ REST · JSON · Bearer JWT
┌────────────────────────────▼─────────────────────────────────────┐
│                    Application layer                             │
│                    FastAPI (app v1.4.0)                          │
│  auth · jobs · matching · llm · meetings · admin · recruiters    │
└────────────────────────────┬─────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌───────────────┐   ┌─────────────────┐   ┌──────────────────┐
│ Domain modules│   │ Auth & security │   │ External APIs    │
│ cv · matching │   │ JWT · OAuth 2FA │   │ Google Calendar  │
│ llm · platform│   │ RBAC · audit    │   │ SMTP (optional)  │
└───────┬───────┘   └─────────────────┘   └──────────────────┘
        │
┌───────▼──────────────────────────────────────────────────────────┐
│                    Data layer                                    │
│         PostgreSQL · SQLAlchemy 2 (sync) · Alembic               │
└──────────────────────────────────────────────────────────────────┘
```

**Separation of concerns**

| Layer | Responsibility | Typical files |
|-------|----------------|---------------|
| Routers | HTTP contracts, auth dependencies | `app/routers/*.py` |
| Modules | Business and AI logic | `app/modules/{cv,matching,llm,platform}/` |
| Models / schemas | Persistence and payload validation | `app/models/`, `app/schemas/` |
| Frontend | Role-based UX, API client | `frontend/app/`, `frontend/lib/api.ts` |

---

## 5. Technology stack

### Backend

| Component | Version | Role |
|-----------|---------|------|
| Python | 3.11–3.13 | Runtime |
| FastAPI | 0.115 | REST API |
| Uvicorn | 0.30 | ASGI server |
| SQLAlchemy | 2.0 | ORM (synchronous sessions) |
| Alembic | 1.14 | Schema migrations |
| PostgreSQL | 14+ | Relational store |
| Pydantic | 2.9 | Request/response validation |
| pypdf | 5.1 | PDF text extraction |
| pyotp | 2.9 | TOTP 2FA |
| httpx | 0.28 | OAuth and Google Calendar |
| pytest / Ruff | 8.3 / latest | Tests and linting |

### Frontend

| Component | Version | Role |
|-----------|---------|------|
| Next.js | 15.5 | App Router UI |
| React | 19.1 | Components |
| TypeScript | 5.9 | Static typing |
| Tailwind CSS | 4.3 | Styling |
| Lucide React | 0.561 | Icons |

---

## 6. Repository structure

```
Project/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry, CORS, routers
│   │   ├── auth.py              # JWT, RBAC dependencies
│   │   ├── database.py          # SQLAlchemy engine and sessions
│   │   ├── routers/             # HTTP handlers
│   │   ├── models/              # SQLAlchemy entities
│   │   ├── schemas/             # Pydantic contracts
│   │   └── modules/
│   │       ├── auth/            # Tokens, OAuth, TOTP
│   │       ├── cv/              # Upload, extraction, skills
│   │       ├── matching/        # NLP pipeline and scoring
│   │       ├── llm/             # Explanations + HallucinationGuard
│   │       └── platform/        # Meetings, audit, Calendar
│   ├── tests/                   # pytest suite
│   ├── scripts/                 # SQL helpers, live smoke tests
│   └── requirements.txt
├── frontend/
│   ├── app/                     # Next.js routes
│   ├── components/              # UI (LLM panel, auth, pipeline)
│   ├── lib/                     # API client + token refresh
│   └── providers/               # Auth, theme, notices
└── docs/                        # PFE booklet, UML, ML notes
```

---

## 7. AI matching engine

Implemented in `app/modules/matching/` (pipeline, NLP, score formula, scorer).

```
Candidate profile + CV          Job offer
              \                    /
               \                  /
                ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. Ingestion      Structured fields + extracted CV text     │
│ 2. Preprocessing  Tokens, FR/EN stop-words, normalization   │
│ 3. Features       Skills, TF-IDF vectors, synonym expansion │
│ 4. Scoring        Weighted 6-dimension formula + penalties  │
│ 5. Explanation    Template LLM + HallucinationGuard         │
│ 6. Ranking        Sorted list + label (Excellent → Weak)    │
└─────────────────────────────────────────────────────────────┘
```

### Compatibility formula (implemented)

\[
S = 100 \times (
0.35\,S_{\text{skills}} +
0.25\,S_{\text{experience}} +
0.20\,S_{\text{semantic}} +
0.10\,S_{\text{education}} +
0.05\,S_{\text{location}} +
0.05\,S_{\text{availability}}
)
\]

| Weight | Dimension | Technique |
|--------|-----------|-----------|
| 35% | Skills | Jaccard / coverage + synonym dictionary |
| 25% | Experience | Profile experience vs job description |
| 20% | Semantic | TF-IDF cosine similarity CV ↔ offer |
| 10% | Education | Field of study vs job text |
| 5% | Location | Geographic alignment |
| 5% | Availability | Internship / employment type fit |

Penalties (incomplete CV, critical missing skills, location mismatch) are applied **multiplicatively** on \(S\).

Trace the pipeline at runtime: `GET /matching/pipeline` and `POST /matching/pipeline/run`.

---

## 8. Explainable LLM and HallucinationGuard

### Why a custom LLM module?

A remote GPT can **invent** skills, overstate expertise, or hide uncertainty. For recruitment, that is unacceptable.

MatiousHire uses a **four-layer grounded architecture**:

| Layer | Component | Function |
|-------|-----------|----------|
| 1. Source of truth | Matching `ScoreBreakdown` | Numeric scores exist before any sentence is written |
| 2. Grounded generation | `app/modules/llm/explanation.py` | Templates and rules; no free-form generation |
| 3. Guard | `app/modules/llm/guard.py` | Skill whitelist, speculative-language filter, confidence |
| 4. Human-in-the-loop | UI + disclaimer | Recruiter remains decision-maker |

### Guard outputs (API)

| Field | Role |
|-------|------|
| `explanation` | Sanitized compatibility text |
| `confidence_score` | 0–100 reliability |
| `grounded` | True if text passed source checks |
| `guard_warnings` | Speculative language, incomplete CV, ungrounded skills |
| `grounded_sources` | Trace (`profile:…`, `job:…`, `score:…`) |
| `disclaimer` | “AI assists; the recruiter decides” |

Inspect architecture live: **`GET /llm/module`** → `anti_hallucination`.

---

## 9. Security model

| Control | Implementation |
|---------|----------------|
| Passwords | PBKDF2-SHA256 |
| Sessions | Short-lived access JWT + rotated refresh tokens |
| Authorization | RBAC: `student`, `candidate`, `recruiter`, `admin` |
| 2FA | TOTP (`pyotp`) |
| Social login | OAuth 2.0 (Google, GitHub, LinkedIn) — optional |
| Enterprise SSO | OpenID Connect — optional |
| Audit | Login and privileged actions in `audit_logs` |
| CORS | Explicit origins; `ALLOW_ALL_CORS=1` for local only |

---

## 10. API domain architecture

Interactive schema: **http://127.0.0.1:8000/docs**  
Protected routes: `Authorization: Bearer <access_token>`

| Prefix | Representative endpoints | Purpose |
|--------|--------------------------|---------|
| `/` | `GET /` | Health (`status: ok`, version 1.4.0) |
| `/auth` | `POST /auth/login`, `/refresh`, `/2fa/*`, OAuth | Identity |
| `/students` | `GET /students/me`, `POST /students/me/cv` | Student workspace |
| `/candidates` | `GET /candidates/me`, applications, saved jobs | Candidate workspace |
| `/recruiters` | `GET /recruiters/jobs/{id}/candidates` | Pipeline |
| `/jobs` | `GET /jobs/`, `POST /jobs/` | Offers |
| `/matching` | `POST /matching/score`, `GET /matching/pipeline` | Compatibility |
| `/llm` | `POST /llm/explain`, `GET /llm/module` | Grounded explanations |
| `/meetings` | confirm / refuse / cancel, Google Calendar | Interviews |
| `/admin` | dashboard, users, audit logs | Supervision |

---

## 11. User roles and frontend routes

| Role | Audience | Routes |
|------|----------|--------|
| `student` | Internship seekers | `/student/profile`, `/student/jobs`, `/student/dashboard`, `/student/interviews` |
| `candidate` | Job seekers | `/candidate/profile`, `/candidate/jobs`, `/candidate/dashboard`, `/candidate/interviews` |
| `recruiter` | Talent acquisition | `/recruiter/dashboard`, `/recruiter/jobs`, `/recruiter/pipeline`, `/recruiter/meetings` |
| `admin` | Operators | `/admin/dashboard`, `/admin/users`, `/admin/audit-logs` |

Public: `/`, `/login`, `/login/oauth/callback`

---

## 12. Installation and quick start

### Prerequisites

Python 3.11–3.13 · Node.js 20+ · PostgreSQL 14+ · Git

### Database

```sql
CREATE DATABASE recruitment_db;
```

```powershell
psql -U postgres -d recruitment_db -f Project\backend\scripts\ensure_auth_tables.sql
```

### Backend

```powershell
cd Project\backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
# Edit DATABASE_URL and SECRET_KEY
alembic -c alembic.ini upgrade head
$env:ALLOW_ALL_CORS = "1"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend

```powershell
cd Project\frontend
npm install
Copy-Item .env.local.example .env.local
npm run dev
```

### Demo accounts

Password: **`Password123`**

| Role | Email |
|------|-------|
| Student | `student.demo2026@example.com` |
| Candidate | `candidate.demo2026@example.com` |
| Recruiter | `recruiter.demo2026@example.com` |
| Admin | `admin@matioushire.com` |

---

## 13. Quality assurance

```powershell
# Backend
cd Project\backend
.\.venv\Scripts\Activate.ps1
ruff check app tests
pytest -q
python scripts\test_app_live.py   # API must be running

# Frontend
cd Project\frontend
npm run verify    # ESLint + TypeScript
```

| Check | Expected |
|-------|----------|
| pytest | 55+ tests passing |
| Live smoke | `scripts/test_app_live.py` — 22 checks |
| Frontend | `npm run verify` — 0 warnings |

Do **not** run `npm run build` while `npm run dev` is active (Windows `.next` cache). Recover with `npm run dev:fresh`.

---

## 14. Jury demo protocol

**Duration:** ~15 minutes · **Servers:** frontend :3000, API :8000

| Block | Time | Actions |
|-------|------|---------|
| A. Health | 2 min | `GET /` → `status: ok`. Open `/docs`. Show `GET /llm/module`. |
| B. Candidate | 5 min | Login (demo student/candidate). Upload PDF CV. Open recommendations. Show AI panel: `confidence_score`, `grounded_sources`, `guard_warnings`. |
| C. Recruiter | 5 min | Login recruiter. Pipeline ranked by score. Open explanation. Shortlist or invite. Optional Calendar status. |
| D. Defense | 3 min | Formula + HallucinationGuard layers. `pytest -q`. Admin audit logs. |

**Evaluation mapping**

| Criterion | Evidence |
|-----------|----------|
| Functionality | Full flows: CV → matching → explain → interview |
| Robustness | pytest, error handlers, token refresh |
| Explainable AI | Breakdown, guard, `GET /llm/module` |
| Reproducibility | This booklet, `.env.example`, smoke script |
| Documentation | `docs/`, UML in `docs/uml/` |

---

## 15. Academic notice

This work is a **Projet de Fin d’Études (PFE 2026)**. It is intended for academic defense and demonstration.

Before any production use: rotate `SECRET_KEY`, restrict CORS, and store OAuth/SMTP secrets outside the repository.

### Related documents

| File | Content |
|------|---------|
| [`PFE_FONCTIONNALITES.md`](PFE_FONCTIONNALITES.md) | Feature catalogue (FR) |
| [`PFE_ML_NLP_MATCHING.md`](PFE_ML_NLP_MATCHING.md) | Matching formulas (FR) |
| [`PFE_LLM_INTEGRATION.md`](PFE_LLM_INTEGRATION.md) | LLM module (FR) |
| [`PFE_COUCHE_DONNEES.md`](PFE_COUCHE_DONNEES.md) | Data layer (FR) |
| [`uml/`](uml/) | PlantUML diagrams |
| [`../README.md`](../README.md) | Developer quick start |

---

**MatiousHire** — Smart recruitment with explainable, grounded AI.
