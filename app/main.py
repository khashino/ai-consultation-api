import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.dependencies import chat_repository
from app.routers import admin, chat, documents, health, pages, rag


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def create_app() -> FastAPI:
    api = FastAPI(
        title="AI Consultation API",
        description=(
            "A local RAG-based AI consultation API using FastAPI, Ollama, "
            "ChromaDB, embeddings, document upload, backend guardrails, "
            "embeddable chatbot, SQLite chat persistence, and admin dashboard."
        ),
        version=settings.app_version
    )

    api.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Learning mode. Restrict in production.
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api.mount("/static", StaticFiles(directory="static"), name="static")

    api.include_router(health.router)
    api.include_router(pages.router)
    api.include_router(documents.router)
    api.include_router(rag.router)
    api.include_router(chat.router)
    api.include_router(admin.router)

    @api.on_event("startup")
    def startup_event():
        chat_repository.init_db()
        logging.info("SQLite chat database initialized at: %s", settings.chat_db_path)

    return api


app = create_app()