from fastapi import APIRouter, File, HTTPException, UploadFile

from app.dependencies import document_service, vector_store_service
from app.models.schemas import UploadResponse


router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    result = await document_service.upload_and_ingest(file)

    return UploadResponse(
        message="Document uploaded and ingested successfully.",
        filename=result["filename"],
        chunks=result["chunks"],
        status=result["status"]
    )


@router.get("")
def list_documents():
    return vector_store_service.list_documents()


@router.delete("/{source}")
def delete_document(source: str):
    return document_service.delete_document(source)