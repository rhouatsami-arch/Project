import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, jobs, recruiters, students


app = FastAPI(
    title="Recruitment API",
    version="1.0.0",
    description="A focused backend for students, recruiters, jobs, applications, CVs, and interviews.",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(recruiters.router)
app.include_router(jobs.router)


@app.get("/", tags=["health"])
def health():
    return {"status": "ok", "app": "Recruitment API", "version": "1.0.0"}
