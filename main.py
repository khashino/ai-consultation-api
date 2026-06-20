import json
import logging
import os
from pathlib import Path
from typing import List, Literal, Optional

import chromadb
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError
from sentence_transformers import SentenceTransformer


load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

CHROMA_DIR = os.getenv("CHROMA_DIR", "chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "consultation_knowledge")
KNOWLEDGE_DIR = os.getenv("KNOWLEDGE_DIR", "knowledge_base")

EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

TOP_K = int(os.getenv("TOP_K", "3"))
MAX_DISTANCE = float(os.getenv("MAX_DISTANCE", "20"))

MAX_CHAT_MESSAGES = int(os.getenv("MAX_CHAT_MESSAGES", "8"))
CHAT_SESSIONS = {}

Path(KNOWLEDGE_DIR).mkdir(parents=True, exist_ok=True)
Path("static").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

app = FastAPI(
    title="AI Consultation API",
    description=(
        "A local RAG-based AI consultation API using FastAPI, Ollama, "
        "ChromaDB, embeddings, document upload, backend guardrails, "
        "and embeddable chatbot memory."
    ),
    version="1.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Learning mode. Restrict this in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

logging.info("Loading embedding model: %s", EMBEDDING_MODEL_NAME)
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
knowledge_collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)


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
    sources: List[str] = []


class RetrievedContext(BaseModel):
    source: str
    chunk_index: int
    distance: float
    content: str


class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks: int
    status: str


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=3)
    message: str = Field(..., min_length=1)
    topic: str = "general"
    user_country: Optional[str] = None
    target_country: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str


def chunk_text(text: str, chunk_size: int = 700, overlap: int = 100) -> List[str]:
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def ingest_text_document(filename: str, text: str) -> dict:
    chunks = chunk_text(text)

    if not chunks:
        raise ValueError("Document is empty or could not be chunked.")

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

        embedding = embedding_model.encode(chunk).tolist()
        embeddings.append(embedding)

    knowledge_collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    return {
        "filename": filename,
        "chunks": len(chunks),
        "status": "ingested"
    }


def retrieve_context(question: str) -> List[RetrievedContext]:
    query_embedding = embedding_model.encode(question).tolist()

    results = knowledge_collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K
    )

    retrieved_contexts = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for document, metadata, distance in zip(documents, metadatas, distances):
        if distance <= MAX_DISTANCE:
            retrieved_contexts.append(
                RetrievedContext(
                    source=metadata.get("source", "unknown"),
                    chunk_index=metadata.get("chunk_index", -1),
                    distance=float(distance),
                    content=document
                )
            )

    return retrieved_contexts


def get_chat_history_text(session_id: str) -> str:
    messages = CHAT_SESSIONS.get(session_id, [])

    if not messages:
        return "No previous conversation."

    recent_messages = messages[-MAX_CHAT_MESSAGES:]

    return "\n".join(
        [
            f"{message['role']}: {message['content']}"
            for message in recent_messages
        ]
    )


def save_chat_turn(session_id: str, user_message: str, assistant_answer: str) -> None:
    if session_id not in CHAT_SESSIONS:
        CHAT_SESSIONS[session_id] = []

    CHAT_SESSIONS[session_id].append(
        {
            "role": "user",
            "content": user_message
        }
    )

    CHAT_SESSIONS[session_id].append(
        {
            "role": "assistant",
            "content": assistant_answer
        }
    )

    CHAT_SESSIONS[session_id] = CHAT_SESSIONS[session_id][-MAX_CHAT_MESSAGES:]


def build_prompt(
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


def build_chat_prompt(
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

    chat_history = get_chat_history_text(request.session_id)

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


def extract_json_from_text(text: str) -> dict:
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
        raise ValueError(
            f"Invalid JSON from model: {str(error)} | Raw output: {raw_output}"
        )


def clean_sources(
    model_sources: List[str],
    retrieved_contexts: List[RetrievedContext]
) -> List[str]:
    valid_sources = {item.source for item in retrieved_contexts}

    cleaned = [
        source for source in model_sources
        if source in valid_sources
    ]

    if cleaned:
        return sorted(set(cleaned))

    return sorted(valid_sources)


def clean_suggested_steps(response: ConsultationResponse) -> ConsultationResponse:
    bad_steps = {"step 1", "step 2", "step 3", "string"}

    normalized_steps = {
        step.strip().lower()
        for step in response.suggested_next_steps
    }

    if normalized_steps.intersection(bad_steps):
        response.suggested_next_steps = [
            "Check the relevant source document",
            "Ask a more specific question",
            "Request human review if needed"
        ]

        if response.confidence == "high":
            response.confidence = "low"

    return response


def apply_safety_guardrails(
    request: ConsultationRequest,
    response: ConsultationResponse
) -> ConsultationResponse:
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
        "message": "AI Consultation API with RAG and chatbot memory is running",
        "model": OLLAMA_MODEL,
        "embedding_model": EMBEDDING_MODEL_NAME,
        "vector_db": "ChromaDB",
        "collection": COLLECTION_NAME,
        "knowledge_dir": KNOWLEDGE_DIR,
        "top_k": TOP_K,
        "max_distance": MAX_DISTANCE,
        "max_chat_messages": MAX_CHAT_MESSAGES,
        "version": "1.2.0"
    }


@app.get("/app")
def frontend_app():
    return FileResponse("static/index.html")


@app.get("/chat-demo")
def chat_demo():
    return FileResponse("static/embed-demo.html")


@app.post("/documents/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    if not file.filename.endswith(".txt"):
        raise HTTPException(
            status_code=400,
            detail="Only .txt files are supported in this version."
        )

    safe_filename = Path(file.filename).name
    file_path = Path(KNOWLEDGE_DIR) / safe_filename

    content_bytes = await file.read()

    try:
        text = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must be UTF-8 encoded text."
        )

    file_path.write_text(text, encoding="utf-8")

    try:
        result = ingest_text_document(safe_filename, text)
        return UploadResponse(
            message="Document uploaded and ingested successfully.",
            filename=result["filename"],
            chunks=result["chunks"],
            status=result["status"]
        )
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest document: {str(error)}"
        )


@app.get("/documents")
def list_documents():
    try:
        data = knowledge_collection.get(
            include=["metadatas"]
        )

        metadatas = data.get("metadatas", [])
        document_map = {}

        for metadata in metadatas:
            source = metadata.get("source", "unknown")

            if source not in document_map:
                document_map[source] = 0

            document_map[source] += 1

        documents = [
            {
                "source": source,
                "chunks": chunks
            }
            for source, chunks in sorted(document_map.items())
        ]

        return {
            "collection": COLLECTION_NAME,
            "total_documents": len(documents),
            "documents": documents
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents: {str(error)}"
        )


@app.delete("/documents/{source}")
def delete_document(source: str):
    try:
        data = knowledge_collection.get(
            where={"source": source},
            include=["metadatas"]
        )

        ids = data.get("ids", [])

        if not ids:
            raise HTTPException(
                status_code=404,
                detail=f"No document found with source: {source}"
            )

        knowledge_collection.delete(ids=ids)

        file_path = Path(KNOWLEDGE_DIR) / source

        file_deleted = False
        if file_path.exists():
            file_path.unlink()
            file_deleted = True

        return {
            "message": "Document deleted successfully.",
            "source": source,
            "deleted_chunks": len(ids),
            "file_deleted": file_deleted
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(error)}"
        )


@app.post("/search", response_model=List[RetrievedContext])
def search_knowledge_base(request: ConsultationRequest):
    return retrieve_context(request.question)


@app.post("/ask", response_model=ConsultationResponse)
def ask_consultation(request: ConsultationRequest):
    retrieved_contexts = retrieve_context(request.question)
    prompt = build_prompt(request, retrieved_contexts)

    try:
        raw_output, ai_output = call_ollama(prompt)
        validated_response = ConsultationResponse(**ai_output)

        validated_response.sources = clean_sources(
            model_sources=validated_response.sources,
            retrieved_contexts=retrieved_contexts
        )

        validated_response = clean_suggested_steps(validated_response)

        safe_response = apply_safety_guardrails(
            request=request,
            response=validated_response
        )

        return safe_response

    except ValidationError as error:
        return fallback_response(f"Schema validation failed: {str(error)}")

    except ValueError as error:
        return fallback_response(str(error))


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    retrieved_contexts = retrieve_context(request.message)
    prompt = build_chat_prompt(request, retrieved_contexts)

    try:
        raw_output, parsed_output = call_ollama(prompt)
        answer = str(parsed_output.get("answer", "")).strip()

        if not answer:
            answer = "I could not generate a reliable answer."

    except Exception as error:
        logging.warning("Chat fallback used. Reason: %s", str(error))
        answer = "I could not generate a reliable answer."

    save_chat_turn(
        session_id=request.session_id,
        user_message=request.message,
        assistant_answer=answer
    )

    return ChatResponse(
        session_id=request.session_id,
        answer=answer
    )


@app.get("/chat/sessions")
def list_chat_sessions():
    return {
        "total_sessions": len(CHAT_SESSIONS),
        "sessions": [
            {
                "session_id": session_id,
                "messages": len(messages)
            }
            for session_id, messages in CHAT_SESSIONS.items()
        ]
    }


@app.get("/chat/sessions/{session_id}")
def get_chat_session(session_id: str):
    return {
        "session_id": session_id,
        "messages": CHAT_SESSIONS.get(session_id, [])
    }


@app.delete("/chat/sessions/{session_id}")
def delete_chat_session(session_id: str):
    if session_id in CHAT_SESSIONS:
        del CHAT_SESSIONS[session_id]
        return {
            "message": "Chat session deleted.",
            "session_id": session_id
        }

    raise HTTPException(
        status_code=404,
        detail=f"No chat session found: {session_id}"
    )


@app.post("/debug")
def debug_consultation(request: ConsultationRequest):
    retrieved_contexts = retrieve_context(request.question)
    prompt = build_prompt(request, retrieved_contexts)

    try:
        raw_output, parsed_output = call_ollama(prompt)

        return {
            "model": OLLAMA_MODEL,
            "embedding_model": EMBEDDING_MODEL_NAME,
            "retrieved_contexts": [
                item.model_dump() for item in retrieved_contexts
            ],
            "prompt": prompt,
            "raw_output": raw_output,
            "parsed_output": parsed_output
        }

    except Exception as error:
        return {
            "model": OLLAMA_MODEL,
            "embedding_model": EMBEDDING_MODEL_NAME,
            "retrieved_contexts": [
                item.model_dump() for item in retrieved_contexts
            ],
            "prompt": prompt,
            "raw_output": str(error),
            "parsed_output": None
        }