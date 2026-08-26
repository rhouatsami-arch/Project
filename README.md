# MatiousHire

**Intelligent HR & Recruitment Platform — PFE 2026**

End-to-end recruitment platform: CV ingestion, multi-criteria NLP matching, explainable AI with an anti-hallucination guard, interview scheduling, and optional Google Calendar sync.

| Service | URL |
|---------|-----|
| Frontend | http://127.0.0.1:3000 |
| Backend API | http://127.0.0.1:8000 |
| OpenAPI | http://127.0.0.1:8000/docs |

**Official PFE booklet (jury):** [`docs/PFE_DOCUMENTATION.md`](docs/PFE_DOCUMENTATION.md)

---

## What this project does

Recruiters cannot triage large CV volumes reliably by hand. Candidates cannot see *why* a job matches. MatiousHire computes a **transparent compatibility score** (six weighted dimensions), then explains it in natural language **without inventing skills**.

The “LLM” is **not** ChatGPT. It is a hybrid module (`app/modules/llm/`) that verbalizes matching scores and runs them through `HallucinationGuard`.

---

## Architecture (summary)

```
Next.js 15  ──REST/JWT──►  FastAPI 1.4.0  ──SQLAlchemy──►  PostgreSQL
                                │
                    cv · matching · llm · meetings · auth
```

**Score**

```
S = 0.35×skills + 0.25×experience + 0.20×semantic(TF-IDF)
  + 0.10×education + 0.05×location + 0.05×availability
```

---

## Stack

| Layer | Technologies |
|-------|----------------|
| Frontend | Next.js 15.5, React 19, TypeScript 5.9, Tailwind 4.3 |
| Backend | FastAPI 0.115, Uvicorn, SQLAlchemy 2, Alembic, Pydantic 2 |
| Data | PostgreSQL 14+ |
| AI | Custom NLP pipeline + grounded LLM + HallucinationGuard |
| QA | pytest (55+), Ruff, ESLint |

---

## Quick start (PowerShell)

**1. Database**

```sql
CREATE DATABASE recruitment_db;
```

**2. Backend**

```powershell
cd Project\backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
$env:ALLOW_ALL_CORS = "1"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**3. Frontend**

```powershell
cd Project\frontend
npm install
Copy-Item .env.local.example .env.local
npm run dev
```

Demo password: **`Password123`**  
`student.demo2026@example.com` · `candidate.demo2026@example.com` · `recruiter.demo2026@example.com` · `admin@matioushire.com`

---

## Tests

```powershell
cd Project\backend
ruff check app tests
pytest -q

cd Project\frontend
npm run verify
```

---

## Documentation map

| Document | Audience |
|----------|----------|
| [docs/PFE_DOCUMENTATION.md](docs/PFE_DOCUMENTATION.md) | **Jury — official booklet** |
| [docs/PFE_ML_NLP_MATCHING.md](docs/PFE_ML_NLP_MATCHING.md) | Matching formulas (FR) |
| [docs/PFE_LLM_INTEGRATION.md](docs/PFE_LLM_INTEGRATION.md) | LLM + guard (FR) |
| [docs/PFE_FONCTIONNALITES.md](docs/PFE_FONCTIONNALITES.md) | Feature list (FR) |
| [docs/uml/](docs/uml/) | PlantUML diagrams |

---

## Academic context

PFE 2026. Rotate secrets before any production deployment.

**MatiousHire** — Explainable, grounded recruitment AI.
