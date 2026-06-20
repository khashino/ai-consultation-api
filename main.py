import json
import logging
import os
from typing import List, Literal, Optional

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ValidationError


load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

app = FastAPI(
    title="AI Consultation API",
    description="A local AI consultation API using FastAPI, Ollama, and structured output validation.",
    version="0.3.0"
)


class ConsultationRequest(BaseModel):
    question: str = Field(..., min_length=5)
    topic: str = Field(..., min_length=2)
    user_country: Optional[str] = None
    target_country: Optional[str] = None


class ConsultationResponse(BaseModel):
    answer: str
    confidence: Literal["low", "medium", "high"]
    needs_human_review: bool
    suggested_next_steps: List[str]


class DebugResponse(BaseModel):
    model: str
    prompt: str
    raw_output: str
    parsed_output: Optional[dict]


def build_prompt(request: ConsultationRequest) -> str:
    return f"""
You are an AI consultation assistant inside a backend API.

Your task:
Return a structured JSON response for the user's question.

Important safety rules:
- Do not make final legal, immigration, medical, financial, or contract decisions.
- If the question involves immigration, law, money, health, contracts, or important personal decisions, set needs_human_review to true.
- If information is missing, say that more details are needed.
- Keep the answer practical and short.
- Do not invent official rules, laws, dates, prices, or guarantees.
- Do not use markdown.
- Do not add any text before or after the JSON.
- Return only valid JSON.

The JSON must have exactly these fields:
{{
  "answer": "string",
  "confidence": "low | medium | high",
  "needs_human_review": true,
  "suggested_next_steps": ["string", "string", "string"]
}}

Field rules:
- confidence must be exactly one of: low, medium, high
- needs_human_review must be true or false
- suggested_next_steps must contain 3 to 5 short practical steps

User context:
- Topic: {request.topic}
- User country: {request.user_country or "not provided"}
- Target country: {request.target_country or "not provided"}

User question:
{request.question}
""".strip()


def extract_json_from_text(text: str) -> dict:
    """
    Tries to parse JSON directly first.
    If the model adds extra text, tries to extract the first JSON object.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model output.")

    json_text = text[start:end + 1]
    return json.loads(json_text)


def fallback_response(reason: str) -> ConsultationResponse:
    """
    Safe fallback when the local model returns bad JSON or invalid schema.
    """
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
        ]
    )


def call_ollama(prompt: str) -> tuple[str, dict]:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.2
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
    except requests.RequestException as error:
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to Ollama: {str(error)}"
        )

    data = response.json()
    raw_output = data.get("response", "")

    logging.info("Raw model output: %s", raw_output)

    try:
        parsed_output = extract_json_from_text(raw_output)
        return raw_output, parsed_output
    except Exception as error:
        raise ValueError(f"Invalid JSON from model: {str(error)} | Raw output: {raw_output}")

def apply_safety_guardrails(
    request: ConsultationRequest,
    response: ConsultationResponse
) -> ConsultationResponse:
    """
    Enforces deterministic business/safety rules after the LLM response.
    This protects the application when the model is overconfident or ignores instructions.
    """

    text_to_check = f"{request.topic} {request.question}".lower()

    sensitive_categories = {
        "immigration": [
            "immigration",
            "visa",
            "work visa",
            "residence permit",
            "embassy",
            "migration"
        ],
        "legal": [
            "law",
            "legal",
            "contract",
            "lawyer",
            "court",
            "lawsuit",
            "agreement"
        ],
        "medical": [
            "medical",
            "health",
            "doctor",
            "medicine",
            "treatment",
            "diagnosis"
        ],
        "financial": [
            "financial",
            "investment",
            "tax",
            "loan",
            "insurance",
            "bank",
            "money"
        ]
    }

    detected_category = None

    for category, keywords in sensitive_categories.items():
        if any(keyword in text_to_check for keyword in keywords):
            detected_category = category
            break

    if detected_category:
        response.needs_human_review = True

        if response.confidence == "high":
            response.confidence = "medium"

        risky_phrases = [
            "yes, you can",
            "you are eligible",
            "you qualify",
            "definitely",
            "guaranteed",
            "approved",
            "you should sign",
            "you do not need a lawyer"
        ]

        answer_lower = response.answer.lower()
        has_risky_answer = any(phrase in answer_lower for phrase in risky_phrases)

        if has_risky_answer:
            response.confidence = "low"

            if detected_category == "immigration":
                response.answer = (
                    "This may be possible, but eligibility cannot be confirmed from the provided information alone. "
                    "Immigration decisions depend on official requirements, your documents, job offer status, "
                    "education, experience, and the specific visa category."
                )

            elif detected_category == "legal":
                response.answer = (
                    "This cannot be safely confirmed from the provided information alone. "
                    "Legal or contract decisions depend on the full contract text, local laws, obligations, risks, "
                    "and your specific situation."
                )

            elif detected_category == "medical":
                response.answer = (
                    "This cannot be safely assessed from the provided information alone. "
                    "Medical decisions depend on symptoms, history, examination, and advice from a qualified clinician."
                )

            elif detected_category == "financial":
                response.answer = (
                    "This cannot be safely confirmed from the provided information alone. "
                    "Financial decisions depend on your goals, risk tolerance, local regulations, and personal situation."
                )

    return response

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "AI Consultation API with Ollama is running",
        "model": OLLAMA_MODEL,
        "version": "0.3.0"
    }


@app.post("/ask", response_model=ConsultationResponse)
def ask_consultation(request: ConsultationRequest):
    prompt = build_prompt(request)

    try:
        raw_output, ai_output = call_ollama(prompt)
        validated_response = ConsultationResponse(**ai_output)

        safe_response = apply_safety_guardrails(
            request=request,
            response=validated_response
        )

        return safe_response

    except ValidationError as error:
        return fallback_response(f"Schema validation failed: {str(error)}")

    except ValueError as error:
        return fallback_response(str(error))


@app.post("/debug", response_model=DebugResponse)
def debug_consultation(request: ConsultationRequest):
    """
    Debug endpoint for learning.
    Shows prompt, raw model output, and parsed JSON.
    Do not expose this endpoint in production.
    """
    prompt = build_prompt(request)

    try:
        raw_output, parsed_output = call_ollama(prompt)
        return DebugResponse(
            model=OLLAMA_MODEL,
            prompt=prompt,
            raw_output=raw_output,
            parsed_output=parsed_output
        )
    except Exception as error:
        return DebugResponse(
            model=OLLAMA_MODEL,
            prompt=prompt,
            raw_output=str(error),
            parsed_output=None
        )