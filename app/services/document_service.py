from pathlib import Path
from typing import List

from fastapi import HTTPException, UploadFile

from app.core.config import settings
from app.services.vector_store_service import VectorStoreService


class DocumentService:
    def __init__(self, vector_store_service: VectorStoreService) -> None:
        self.vector_store_service = vector_store_service

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 700,
        overlap: int = 100
    ) -> List[str]:
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start += chunk_size - overlap

        return chunks

    async def upload_and_ingest(self, file: UploadFile) -> dict:
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename is required."
            )

        if not file.filename.endswith(".txt"):
            raise HTTPException(
                status_code=400,
                detail="Only .txt files are supported in this version."
            )

        safe_filename = Path(file.filename).name
        file_path = Path(settings.knowledge_dir) / safe_filename

        content_bytes = await file.read()

        try:
            text = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="File must be UTF-8 encoded text."
            )

        file_path.write_text(text, encoding="utf-8")

        chunks = self.chunk_text(text)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="Document is empty or could not be chunked."
            )

        chunk_count = self.vector_store_service.upsert_chunks(
            filename=safe_filename,
            chunks=chunks
        )

        return {
            "filename": safe_filename,
            "chunks": chunk_count,
            "status": "ingested"
        }

    def delete_document(self, source: str) -> dict:
        deleted_chunks = self.vector_store_service.delete_document(source)

        if deleted_chunks == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No document found with source: {source}"
            )

        file_path = Path(settings.knowledge_dir) / source

        file_deleted = False
        if file_path.exists():
            file_path.unlink()
            file_deleted = True

        return {
            "message": "Document deleted successfully.",
            "source": source,
            "deleted_chunks": deleted_chunks,
            "file_deleted": file_deleted
        }