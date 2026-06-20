from typing import List

from fastapi import APIRouter

from app.dependencies import rag_service, vector_store_service
from app.models.schemas import (
    ConsultationRequest,
    ConsultationResponse,
    RetrievedContext,
)


router = APIRouter(tags=["RAG"])


@router.post("/search", response_model=List[RetrievedContext])
def search_knowledge_base(request: ConsultationRequest):
    return vector_store_service.search(request.question)


@router.post("/ask", response_model=ConsultationResponse)
def ask_consultation(request: ConsultationRequest):
    return rag_service.ask(request)


@router.post("/debug")
def debug_consultation(request: ConsultationRequest):
    return rag_service.debug(request)