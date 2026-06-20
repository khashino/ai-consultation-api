from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.security import require_admin
from app.dependencies import ollama_service


router = APIRouter(prefix="/admin", tags=["Admin"])


class SetModelRequest(BaseModel):
    model_name: str = Field(..., min_length=1)


@router.get("/models")
def list_ollama_models(_: str = Depends(require_admin)):
    return ollama_service.list_models()


@router.post("/model")
def set_ollama_model(
    request: SetModelRequest,
    _: str = Depends(require_admin),
):
    return ollama_service.set_model(request.model_name)