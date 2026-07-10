from fastapi import FastAPI
from app.database import Base, engine
from app.routers import (
    auth, students, recruiters, candidates,
    admin, users, jobs, cv, matching,
    recommendations, ai_explain, meetings, logs, quiz
)
Base.metadata.create_all(bind=engine)
app = FastAPI(title="MatiousHire", version="2.0.0",
    description="AI-powered recruitment platform")

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(recruiters.router)
app.include_router(candidates.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(jobs.router)
app.include_router(cv.router)
app.include_router(matching.router)
app.include_router(recommendations.router)
app.include_router(ai_explain.router)
app.include_router(meetings.router)
app.include_router(logs.router)
app.include_router(quiz.router)

@app.get("/", tags=["health"])
def health():
    return {"status": "ok", "app": "MatiousHire", "version": "2.0.0"}
