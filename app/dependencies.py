from app.repositories.chat_repository import ChatRepository
from app.services.chat_service import ChatService
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService
from app.services.guardrail_service import GuardrailService
from app.services.ollama_service import OllamaService
from app.services.rag_service import RagService
from app.services.vector_store_service import VectorStoreService


embedding_service = EmbeddingService()
vector_store_service = VectorStoreService(embedding_service)
ollama_service = OllamaService()
guardrail_service = GuardrailService()
chat_repository = ChatRepository()

document_service = DocumentService(vector_store_service)

rag_service = RagService(
    vector_store_service=vector_store_service,
    ollama_service=ollama_service,
    guardrail_service=guardrail_service
)

chat_service = ChatService(
    chat_repository=chat_repository,
    vector_store_service=vector_store_service,
    ollama_service=ollama_service
)