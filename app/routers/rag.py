from typing import List

from fastapi import APIRouter, Depends

from app.core.security import require_admin
from app.dependencies import rag_service, vector_store_service
from app.models.schemas import (
    ConsultationRequest,
    ConsultationResponse,
    RetrievedContext,
)


router = APIRouter(tags=["RAG"])


@router.post("/search", response_model=List[RetrievedContext])
def search_knowledge_base(request: ConsultationRequest):
    """
    Public for now.

    Later you can protect this if you want the whole RAG API to be admin-only.
    """
    return vector_store_service.search(request.question)


@router.post("/ask", response_model=ConsultationResponse)
def ask_consultation(request: ConsultationRequest):
    """
    Public for now.

    Useful while testing the project and API docs.
    """
    return rag_service.ask(request)


@router.post("/debug")
def debug_consultation(
    request: ConsultationRequest,
    _: str = Depends(require_admin),
):
    """
    Admin-only because it exposes retrieved context, prompt, and raw model output.
    """
    return rag_service.debug(request)