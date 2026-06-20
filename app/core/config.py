import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

    chroma_dir: str = os.getenv("CHROMA_DIR", "chroma_db")
    collection_name: str = os.getenv("COLLECTION_NAME", "consultation_knowledge")
    knowledge_dir: str = os.getenv("KNOWLEDGE_DIR", "knowledge_base")

    embedding_model_name: str = os.getenv(
        "EMBEDDING_MODEL_NAME",
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    top_k: int = int(os.getenv("TOP_K", "3"))
    max_distance: float = float(os.getenv("MAX_DISTANCE", "20"))

    chat_db_path: str = os.getenv("CHAT_DB_PATH", "chat_history.db")
    max_chat_messages: int = int(os.getenv("MAX_CHAT_MESSAGES", "8"))

    app_version: str = "1.4.0"

    def ensure_directories(self) -> None:
        Path(self.knowledge_dir).mkdir(parents=True, exist_ok=True)
        Path("static").mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()