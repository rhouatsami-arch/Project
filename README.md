# Recruitment Project

This workspace is split into two apps:

- `backend/`: FastAPI API for auth, jobs, applications, saved jobs, CV uploads, candidate matching, and interview invites.
- `frontend/`: React/Vite UI for students and recruiters.

## Backend

```bash
cd backend
../.venv/bin/uvicorn app.main:app --reload
```

API docs:

```text
http://127.0.0.1:8000/docs
```

Database migrations use Alembic:

```bash
cd backend
../.venv/bin/alembic -c alembic.ini upgrade head
```

Create a new migration after changing SQLAlchemy models:

```bash
cd backend
../.venv/bin/alembic -c alembic.ini revision --autogenerate -m "describe change"
../.venv/bin/alembic -c alembic.ini upgrade head
```

## Frontend

```bash
cd frontend
npm run dev
```

UI:

```text
http://127.0.0.1:5173
```

The frontend calls `http://127.0.0.1:8000` by default. To change that, create `frontend/.env`:

```env
VITE_API_URL=http://127.0.0.1:8000
```
