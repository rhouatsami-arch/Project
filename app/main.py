from fastapi import FastAPI
from app.database import Base, engine
from app.routers import auth, students, recruiters

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student–Recruiter API",
    description="Two spaces: students manage their profiles, recruiters browse them.",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(recruiters.router)


@app.get("/", tags=["health"])
def health():
    return {"status": "ok"}
