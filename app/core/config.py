import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


def get_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


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

    app_version: str = "1.5.0"

    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin")

    admin_session_secret: str = os.getenv(
        "ADMIN_SESSION_SECRET",
        "dev-only-change-this-secret"
    )
    admin_cookie_name: str = os.getenv("ADMIN_COOKIE_NAME", "admin_session")
    admin_cookie_secure: bool = get_bool_env("ADMIN_COOKIE_SECURE", False)

    def ensure_directories(self) -> None:
        Path(self.knowledge_dir).mkdir(parents=True, exist_ok=True)
        Path("static").mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()