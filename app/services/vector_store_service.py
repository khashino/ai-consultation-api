from typing import List

import chromadb

from app.core.config import settings
from app.models.schemas import RetrievedContext
from app.services.embedding_service import EmbeddingService


class VectorStoreService:
    def __init__(self, embedding_service: EmbeddingService) -> None:
        self.embedding_service = embedding_service
        self.client = chromadb.PersistentClient(path=settings.chroma_dir)
        self.collection = self.client.get_or_create_collection(
            name=settings.collection_name
        )

    def upsert_chunks(self, filename: str, chunks: List[str]) -> int:
        ids = []
        documents = []
        metadatas = []
        embeddings = []

        for index, chunk in enumerate(chunks):
            chunk_id = f"{filename}_chunk_{index}"

            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append(
                {
                    "source": filename,
                    "chunk_index": index
                }
            )
            embeddings.append(self.embedding_service.embed_text(chunk))

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

        return len(chunks)

    def search(self, question: str) -> List[RetrievedContext]:
        query_embedding = self.embedding_service.embed_text(question)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=settings.top_k
        )

        retrieved_contexts = []

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for document, metadata, distance in zip(documents, metadatas, distances):
            if distance <= settings.max_distance:
                retrieved_contexts.append(
                    RetrievedContext(
                        source=metadata.get("source", "unknown"),
                        chunk_index=metadata.get("chunk_index", -1),
                        distance=float(distance),
                        content=document
                    )
                )

        return retrieved_contexts

    def list_documents(self) -> dict:
        data = self.collection.get(include=["metadatas"])

        metadatas = data.get("metadatas", [])
        document_map = {}

        for metadata in metadatas:
            source = metadata.get("source", "unknown")
            document_map[source] = document_map.get(source, 0) + 1

        documents = [
            {
                "source": source,
                "chunks": chunks
            }
            for source, chunks in sorted(document_map.items())
        ]

        return {
            "collection": settings.collection_name,
            "total_documents": len(documents),
            "documents": documents
        }

    def delete_document(self, source: str) -> int:
        data = self.collection.get(
            where={"source": source},
            include=["metadatas"]
        )

        ids = data.get("ids", [])

        if ids:
            self.collection.delete(ids=ids)

        return len(ids)