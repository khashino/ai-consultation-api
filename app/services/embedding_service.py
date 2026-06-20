import logging

from sentence_transformers import SentenceTransformer

from app.core.config import settings


class EmbeddingService:
    def __init__(self) -> None:
        logging.info("Loading embedding model: %s", settings.embedding_model_name)
        self.model = SentenceTransformer(settings.embedding_model_name)

    def embed_text(self, text: str) -> list:
        return self.model.encode(text).tolist()