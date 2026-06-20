from fastapi import APIRouter

from app.core.config import settings


router = APIRouter(tags=["Health"])


@router.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "AI Consultation API is running",
        "model": settings.ollama_model,
        "embedding_model": settings.embedding_model_name,
        "vector_db": "ChromaDB",
        "collection": settings.collection_name,
        "knowledge_dir": settings.knowledge_dir,
        "top_k": settings.top_k,
        "max_distance": settings.max_distance,
        "chat_db_path": settings.chat_db_path,
        "max_chat_messages": settings.max_chat_messages,
        "version": settings.app_version
    }