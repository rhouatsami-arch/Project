# main.py
from fastapi import FastAPI
from app.routers.routers.routers import user
from app.routers.routers import auth

app = FastAPI()

# Include routers
app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Hello World"}

