import logging
from typing import List

from pydantic import ValidationError

from app.models.schemas import (
    ConsultationRequest,
    ConsultationResponse,
    RetrievedContext,
)
from app.services.guardrail_service import GuardrailService
from app.services.ollama_service import OllamaService
from app.services.vector_store_service import VectorStoreService


class RagService:
    def __init__(
        self,
        vector_store_service: VectorStoreService,
        ollama_service: OllamaService,
        guardrail_service: GuardrailService
    ) -> None:
        self.vector_store_service = vector_store_service
        self.ollama_service = ollama_service
        self.guardrail_service = guardrail_service

    def build_prompt(
        self,
        request: ConsultationRequest,
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

        return f"""
You are a RAG assistant inside a backend API.

You must answer ONLY using the retrieved context.

Important rules:
- Do not answer from general knowledge.
- Do not introduce yourself as a chatbot or computer program.
- If the user asks who you are, say: "I am a RAG assistant that answers using the local knowledge base."
- If the retrieved context does not contain enough information, say: "I can only answer based on the local knowledge base, and I could not find enough relevant information for this question."
- Do not invent facts, laws, prices, dates, requirements, or guarantees.
- Do not make final legal, immigration, medical, financial, or contract decisions.
- If the question involves immigration, law, money, health, contracts, or important personal decisions, set needs_human_review to true.
- Keep the answer practical and short.
- Do not use markdown.
- Do not add any text before or after the JSON.
- Return only valid JSON.

Retrieved context:
{context_text}

User context:
- Topic: {request.topic}
- User country: {request.user_country or "not provided"}
- Target country: {request.target_country or "not provided"}

User question:
{request.question}

Return JSON exactly in this shape:
{{
  "answer": "short practical answer based only on the retrieved context",
  "confidence": "low",
  "needs_human_review": true,
  "suggested_next_steps": [
    "Check the relevant source document",
    "Ask a more specific question",
    "Request human review if needed"
  ],
  "sources": ["source_file_name.txt"]
}}

Field rules:
- confidence must be exactly one of: low, medium, high
- needs_human_review must be true or false
- suggested_next_steps must contain 3 to 5 real practical steps
- suggested_next_steps must not contain placeholder values like "step 1", "step 2", or "step 3"
- sources must contain only file names from the retrieved context
""".strip()

    def fallback_response(self, reason: str) -> ConsultationResponse:
        logging.warning("Using fallback response. Reason: %s", reason)

        return ConsultationResponse(
            answer=(
                "I could not generate a reliable structured answer for this request. "
                "More details and human review are recommended."
            ),
            confidence="low",
            needs_human_review=True,
            suggested_next_steps=[
                "Clarify the exact question",
                "Provide missing background details",
                "Ask a qualified human expert to review the case"
            ],
            sources=[]
        )

    def ask(self, request: ConsultationRequest) -> ConsultationResponse:
        retrieved_contexts = self.vector_store_service.search(request.question)
        prompt = self.build_prompt(request, retrieved_contexts)

        try:
            raw_output, ai_output = self.ollama_service.generate_json(prompt)
            response = ConsultationResponse(**ai_output)

            valid_sources = {item.source for item in retrieved_contexts}

            response.sources = self.guardrail_service.clean_sources(
                model_sources=response.sources,
                valid_sources=valid_sources
            )

            response = self.guardrail_service.clean_suggested_steps(response)

            response = self.guardrail_service.apply_safety_guardrails(
                request=request,
                response=response
            )

            return response

        except ValidationError as error:
            return self.fallback_response(f"Schema validation failed: {str(error)}")

        except Exception as error:
            return self.fallback_response(str(error))

    def debug(self, request: ConsultationRequest) -> dict:
        retrieved_contexts = self.vector_store_service.search(request.question)
        prompt = self.build_prompt(request, retrieved_contexts)

        try:
            raw_output, parsed_output = self.ollama_service.generate_json(prompt)

            return {
                "retrieved_contexts": [
                    item.model_dump() for item in retrieved_contexts
                ],
                "prompt": prompt,
                "raw_output": raw_output,
                "parsed_output": parsed_output
            }

        except Exception as error:
            return {
                "retrieved_contexts": [
                    item.model_dump() for item in retrieved_contexts
                ],
                "prompt": prompt,
                "raw_output": str(error),
                "parsed_output": None
            }