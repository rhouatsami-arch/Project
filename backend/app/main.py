import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.error_handlers import register_error_handlers
from app.models import auth as auth_models  # noqa: F401 — register auth tables
from app.models import (
    platform as platform_models,  # noqa: F401 — register platform tables
)
from app.models import (
    recruitment as recruitment_models,  # noqa: F401 — register recruitment tables
)
from app.routers import (
    admin,
    auth,
    candidate,
    jobs,
    llm,
    matching,
    meetings,
    recruiters,
    students,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Create any missing tables (e.g. after auth schema upgrades)."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema verified")
    yield


app = FastAPI(
    title="MatiousHire API",
    version="1.4.0",
    lifespan=lifespan,
    description=(
        "MatiousHire — Plateforme RH intelligente (PFE 2026):\n\n"
        "- **Métier** : utilisateurs, offres, CV, recommandations, réunions\n"
        "- **IA** : NLP, matching, embeddings, **LLM explicable** "
        "(résumés, explications, compétences manquantes)\n"
        "- **API LLM** : `/llm/explain`, `/llm/module`, résumés CV/offre\n"
    ),
)

# Compute allowed origins from environment (defaults include common local ports)
allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        (
            "http://localhost:3000,http://127.0.0.1:3000,"
            "http://localhost:3001,http://127.0.0.1:3001,"
            "http://localhost:3002,http://127.0.0.1:3002,"
            "http://localhost:5173,http://127.0.0.1:5173"
        ),
    ).split(",")
    if origin.strip()
]

# Allow an easy development override to accept requests from any origin.
# Set `ALLOW_ALL_CORS=1` to enable; leave unset for stricter defaults.
if os.getenv("ALLOW_ALL_CORS", "0") == "1":
    # Use a permissive regex matching localhost and 127.0.0.1 on any port so
    # the CORSMiddleware echoes the exact Origin header (required when
    # credentials are enabled).
    allow_origin_regex = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"
    allow_origins = []
else:
    allow_origin_regex = None

# (no duplicates) - allowed_origins and allow_origin_regex are already
# computed above based on `CORS_ORIGINS` and `ALLOW_ALL_CORS`.

if os.getenv("ALLOW_ALL_CORS", "0") == "1":
    # Lightweight dev middleware that reliably responds to OPTIONS
    # preflight and echoes the request Origin for non-OPTIONS so
    # the browser receives `Access-Control-Allow-Origin` (required
    # when `credentials` are used).
    from fastapi import Request
    from starlette.responses import PlainTextResponse

    @app.middleware("http")
    async def _dev_cors_middleware(request: Request, call_next):
        origin = request.headers.get("origin") or request.headers.get("Origin")
        if origin and (origin.startswith("http://127.0.0.1") or origin.startswith("http://localhost")):
            if request.method == "OPTIONS":
                headers = {
                    "Access-Control-Allow-Origin": origin,
                    "Access-Control-Allow-Methods": "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT",
                    "Access-Control-Allow-Headers": request.headers.get("access-control-request-headers", "*") or "*",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Max-Age": "600",
                }
                return PlainTextResponse("OK", status_code=200, headers=headers)
            response = await call_next(request)
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers.setdefault("Access-Control-Allow-Credentials", "true")
            return response
        return await call_next(request)
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_origin_regex=allow_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

logger.info("CORS configuration: allow_origins=%s allow_origin_regex=%s", allowed_origins, allow_origin_regex)
try:
    with open(os.path.join(os.path.dirname(__file__), '..', '..', '.cors_debug.json'), 'w', encoding='utf-8') as fh:
        import json

        json.dump({'allow_origins': allowed_origins, 'allow_origin_regex': allow_origin_regex}, fh)
except Exception:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
register_error_handlers(app)

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(candidate.router)
app.include_router(recruiters.router)
app.include_router(jobs.router)
app.include_router(matching.router)
app.include_router(meetings.router)
app.include_router(llm.router)
app.include_router(admin.router)


@app.get("/", tags=["health"])
def health():
    return {"status": "ok", "app": "MatiousHire API", "version": app.version}


@app.get("/debug/middleware", tags=["debug"])
def debug_middleware():
    # Return a simple list of user middleware for debugging CORS ordering.
    return {"user_middleware": [m.cls.__name__ for m in app.user_middleware]}
