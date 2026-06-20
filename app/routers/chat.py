from fastapi import APIRouter, HTTPException

from app.dependencies import chat_service
from app.models.schemas import ChatRequest, ChatResponse


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):
    return chat_service.chat(request)


@router.get("/sessions")
def list_chat_sessions():
    return chat_service.list_sessions()


@router.get("/sessions/{session_id}")
def get_chat_session(session_id: str):
    return chat_service.get_session(session_id)


@router.delete("/sessions/{session_id}")
def delete_chat_session(session_id: str):
    result = chat_service.delete_session(session_id)

    if not result["found"]:
        raise HTTPException(
            status_code=404,
            detail=f"No chat session found: {session_id}"
        )

    return {
        "message": "Chat session deleted.",
        "session_id": session_id,
        "deleted_messages": result["deleted_messages"]
    }


@router.get("/messages/recent")
def get_recent_chat_messages(limit: int = 20):
    return chat_service.recent_messages(limit)