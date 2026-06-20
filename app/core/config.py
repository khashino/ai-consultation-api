import json
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

    app_version: str = "1.6.0"

    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin")

    admin_session_secret: str = os.getenv(
        "ADMIN_SESSION_SECRET",
        "dev-only-change-this-secret"
    )
    admin_cookie_name: str = os.getenv("ADMIN_COOKIE_NAME", "admin_session")
    admin_cookie_secure: bool = get_bool_env("ADMIN_COOKIE_SECURE", False)

    runtime_config_path: str = os.getenv("RUNTIME_CONFIG_PATH", "runtime_config.json")

    def ensure_directories(self) -> None:
        Path(self.knowledge_dir).mkdir(parents=True, exist_ok=True)
        Path("static").mkdir(parents=True, exist_ok=True)

    def load_runtime_config(self) -> None:
        path = Path(self.runtime_config_path)

        if not path.exists():
            return

        try:
            data = json.loads(path.read_text(encoding="utf-8"))

            runtime_model = data.get("ollama_model")
            if runtime_model:
                self.ollama_model = runtime_model

        except Exception:
            # Keep .env/default config if runtime config is invalid.
            return

    def save_runtime_config(self) -> None:
        path = Path(self.runtime_config_path)

        data = {
            "ollama_model": self.ollama_model
        }

        path.write_text(
            json.dumps(data, indent=2),
            encoding="utf-8"
        )

    def set_ollama_model(self, model_name: str) -> None:
        self.ollama_model = model_name
        self.save_runtime_config()


settings = Settings()
settings.ensure_directories()
settings.load_runtime_config()