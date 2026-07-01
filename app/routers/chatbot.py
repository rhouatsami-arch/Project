from fastapi import APIRouter
from app.services.chatbot import chat

router = APIRouter(prefix="/chat", tags=["chatbot"])

chat_sessions: dict[str, list] = {}  # In prod: use Redis

@router.post("/message")
def send_message(session_id: str, message: str):
    history = chat_sessions.setdefault(session_id, [])
    reply = chat(history, message)
    return {"reply": reply, "session_id": session_id}

@router.get("/history/{session_id}")
def get_history(session_id: str):
    return chat_sessions.get(session_id, [])