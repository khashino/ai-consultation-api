import logging
from typing import List

from app.core.config import settings
from app.models.schemas import ChatRequest, ChatResponse, RetrievedContext
from app.repositories.chat_repository import ChatRepository
from app.services.ollama_service import OllamaService
from app.services.vector_store_service import VectorStoreService


class ChatService:
    def __init__(
        self,
        chat_repository: ChatRepository,
        vector_store_service: VectorStoreService,
        ollama_service: OllamaService
    ) -> None:
        self.chat_repository = chat_repository
        self.vector_store_service = vector_store_service
        self.ollama_service = ollama_service

    def get_chat_history_text(self, session_id: str) -> str:
        messages = self.chat_repository.get_recent_messages(
            session_id=session_id,
            limit=settings.max_chat_messages
        )

        if not messages:
            return "No previous conversation."

        return "\n".join(
            [
                f"{message['role']}: {message['content']}"
                for message in messages
            ]
        )

    def build_chat_prompt(
        self,
        request: ChatRequest,
        retrieved_contexts: List[RetrievedContext]
    ) -> str:
        if retrieved_contexts:
            context_text = "\n\n".join(
                [
                    f"Source: {item.source}, chunk: {item.chunk_index}\n{item.content}"
                    for item in retrieved_contexts
                ]
            )
        else:
            context_text = "No relevant context was found in the local knowledge base."

        chat_history = self.get_chat_history_text(request.session_id)

        return f"""
You are a helpful RAG chatbot embedded inside a website.

You must answer using:
1. The retrieved context from the local knowledge base
2. The previous conversation only to understand references like "it", "that", "explain more", or "give me examples"

Important rules:
- Do not answer from general knowledge if the retrieved context is not enough.
- If the user asks who you are, say: "I am a RAG assistant that answers using the local knowledge base."
- If the user refers to something from previous conversation, use chat history to understand the reference.
- If the local knowledge base does not contain enough information, say: "I can only answer based on the local knowledge base, and I could not find enough relevant information for this question."
- Do not invent facts, laws, prices, dates, requirements, or guarantees.
- Keep the answer short, friendly, and conversational.
- Do not use markdown.
- Return only valid JSON.
- Do not add text before or after the JSON.

Retrieved context:
{context_text}

Previous conversation:
{chat_history}

User context:
- Topic: {request.topic}
- User country: {request.user_country or "not provided"}
- Target country: {request.target_country or "not provided"}

Current user message:
{request.message}

Return JSON exactly in this shape:
{{
  "answer": "short conversational answer"
}}
""".strip()

    def chat(self, request: ChatRequest) -> ChatResponse:
        retrieved_contexts = self.vector_store_service.search(request.message)
        prompt = self.build_chat_prompt(request, retrieved_contexts)

        self.chat_repository.save_message(
            session_id=request.session_id,
            role="user",
            content=request.message
        )

        try:
            raw_output, parsed_output = self.ollama_service.generate_json(prompt)
            answer = str(parsed_output.get("answer", "")).strip()

            if not answer:
                answer = "I could not generate a reliable answer."

        except Exception as error:
            logging.warning("Chat fallback used. Reason: %s", str(error))
            answer = "I could not generate a reliable answer."

        self.chat_repository.save_message(
            session_id=request.session_id,
            role="assistant",
            content=answer
        )

        return ChatResponse(
            session_id=request.session_id,
            answer=answer
        )

    def list_sessions(self) -> dict:
        sessions = self.chat_repository.list_sessions()

        return {
            "total_sessions": len(sessions),
            "sessions": sessions
        }

    def get_session(self, session_id: str) -> dict:
        return {
            "session_id": session_id,
            "messages": self.chat_repository.get_session(session_id)
        }

    def delete_session(self, session_id: str) -> dict:
        deleted_count = self.chat_repository.delete_session(session_id)

        if deleted_count == 0:
            return {
                "found": False,
                "deleted_messages": 0
            }

        return {
            "found": True,
            "deleted_messages": deleted_count
        }

    def recent_messages(self, limit: int = 20) -> dict:
        return {
            "limit": limit,
            "messages": self.chat_repository.get_recent_messages_all_sessions(limit)
        }