# AI Consultation RAG Platform

A local AI Engineering project that demonstrates how to build a practical Retrieval-Augmented Generation system using FastAPI, Ollama, ChromaDB, SentenceTransformers, SQLite, and an embeddable chatbot widget.

This project started as a simple AI consultation API and evolved into a mini AI product with:

* Local LLM generation with Ollama
* RAG retrieval using ChromaDB
* Multilingual embeddings
* Document upload and ingestion
* Admin dashboard
* Embeddable chatbot widget
* Session-based chat memory
* Persistent chat history with SQLite
* Backend guardrails for safer responses
* Search, debug, and evaluation scripts
* Clean modular backend structure

---

## Project Goal

The goal of this project is to learn and demonstrate practical AI Engineering concepts by building a working local RAG application.

The system allows users to upload knowledge base documents, ask questions about them, and receive AI-generated answers based on retrieved context.

It is designed as a portfolio project for roles such as:

* AI Engineer
* Backend AI Engineer
* LLM Application Developer
* RAG Developer
* AI Automation Engineer
* Enterprise AI Solutions Engineer

---

## Main Features

### 1. RAG Question Answering

The API retrieves relevant document chunks from ChromaDB and sends them to a local Ollama model to generate an answer.

Endpoint:

```text
POST /ask
```

The response includes:

* Answer
* Confidence
* Human review flag
* Suggested next steps
* Sources

---

### 2. Embeddable Chatbot Widget

The project includes a JavaScript chatbot widget that can be embedded into any HTML page.

Example:

```html
<script>
  window.AI_CHATBOT_API_BASE = "http://127.0.0.1:8000";
  window.AI_CHATBOT_TITLE = "RAG Assistant";
  window.AI_CHATBOT_TOPIC = "AI Consultation RAG Knowledge Base";
  window.AI_CHATBOT_USER_COUNTRY = "Iran";
  window.AI_CHATBOT_TARGET_COUNTRY = null;
</script>

<script src="http://127.0.0.1:8000/static/chatbot-widget.js"></script>
```

The chatbot calls:

```text
POST /chat
```

It shows only the final answer to the user.

---

### 3. Persistent Chat Memory

Chat history is stored in SQLite.

The chatbot keeps a session ID in browser localStorage, and the backend stores the conversation in:

```text
chat_history.db
```

This means chat history survives server restarts.

---

### 4. Admin Dashboard

The admin dashboard is available at:

```text
http://127.0.0.1:8000/app
```

It includes:

* System dashboard
* Document upload
* Document listing
* Document deletion
* RAG ask form
* Knowledge base search
* Debug view
* Chat sessions list
* Session history viewer
* Session deletion
* Recent messages view

---

### 5. Document Management

Supported document type:

```text
.txt
```

Documents are uploaded through the admin panel or API.

The system:

1. Saves the file in `knowledge_base/`
2. Splits it into chunks
3. Creates embeddings
4. Stores vectors in ChromaDB

Endpoints:

```text
POST /documents/upload
GET /documents
DELETE /documents/{source}
```

---

### 6. Vector Search

The system can search the ChromaDB knowledge base without calling the LLM.

Endpoint:

```text
POST /search
```

This is useful for debugging RAG retrieval quality.

---

### 7. Backend Guardrails

The project includes backend-level safety rules for sensitive topics such as:

* Immigration
* Legal
* Medical
* Financial

Guardrails can:

* Force human review
* Reduce overconfident answers
* Clean placeholder model output
* Prevent unsafe confidence

This shows an important AI Engineering concept:

```text
Prompts guide the model.
Backend rules protect the product.
```

---

## Current Architecture

```text
User / Admin / Embedded Website
        ↓
FastAPI Backend
        ↓
Routers
        ↓
Services
        ↓
Repositories / Vector DB / LLM
        ↓
Ollama + ChromaDB + SQLite
```

---

## RAG Flow

```text
User question
↓
Embedding model creates query embedding
↓
ChromaDB retrieves relevant chunks
↓
Prompt is built with retrieved context
↓
Ollama generates JSON response
↓
Pydantic validates response
↓
Guardrails clean and adjust response
↓
API returns final answer
```

---

## Chat Flow

```text
User sends message from chatbot
↓
Browser sends session_id + message to /chat
↓
Backend retrieves recent chat history from SQLite
↓
Backend retrieves relevant knowledge from ChromaDB
↓
Prompt combines chat history + retrieved context + latest message
↓
Ollama generates answer
↓
Backend saves user message and assistant answer to SQLite
↓
Widget displays only the answer
```

---

## Project Structure

```text
ai-consultation-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── dependencies.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── chat_repository.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── documents.py
│   │   ├── health.py
│   │   ├── pages.py
│   │   └── rag.py
│   └── services/
│       ├── __init__.py
│       ├── chat_service.py
│       ├── document_service.py
│       ├── embedding_service.py
│       ├── guardrail_service.py
│       ├── ollama_service.py
│       ├── rag_service.py
│       └── vector_store_service.py
├── scripts/
│   ├── __init__.py
│   ├── evaluate_api.py
│   ├── evaluate_retrieval.py
│   ├── ingest_documents.py
│   ├── test_api.py
│   └── test_retrieval.py
├── static/
│   ├── index.html
│   ├── embed-demo.html
│   └── chatbot-widget.js
├── knowledge_base/
├── chroma_db/
├── main.py
├── README.md
├── LOCAL_SETUP.md
├── PROJECT_CONTEXT_FOR_NEXT_CHAT.md
├── requirements.txt
├── .env
├── .env.example
└── .gitignore
```

---

## Folder Explanation

### `app/`

Main backend application package.

### `app/main.py`

Creates the FastAPI app, configures CORS, mounts static files, registers routers, and initializes the SQLite chat database.

### `app/dependencies.py`

Creates shared service instances used by routers.

### `app/core/config.py`

Loads environment variables and stores project settings.

### `app/models/schemas.py`

Contains Pydantic request and response models.

### `app/routers/`

Contains API route definitions.

Routers:

* `health.py` — system health endpoint
* `pages.py` — admin and chatbot demo pages
* `documents.py` — upload, list, delete documents
* `rag.py` — ask, search, debug
* `chat.py` — chatbot and session endpoints

### `app/services/`

Contains business logic.

Services:

* `embedding_service.py` — loads embedding model and creates embeddings
* `vector_store_service.py` — ChromaDB operations
* `document_service.py` — document upload, chunking, ingestion
* `ollama_service.py` — local LLM calls
* `rag_service.py` — RAG prompt and `/ask` logic
* `chat_service.py` — chatbot prompt, memory, `/chat` logic
* `guardrail_service.py` — response cleanup and safety rules

### `app/repositories/`

Contains database access logic.

Currently:

* `chat_repository.py` — SQLite chat persistence

### `static/`

Frontend files.

* `index.html` — admin dashboard
* `embed-demo.html` — sample page using chatbot widget
* `chatbot-widget.js` — embeddable chatbot script

### `scripts/`

Utility scripts for testing and evaluation.

* `test_api.py`
* `test_retrieval.py`
* `evaluate_api.py`
* `evaluate_retrieval.py`
* `ingest_documents.py`

### `knowledge_base/`

Local uploaded text files.

Usually ignored by Git.

### `chroma_db/`

Local ChromaDB vector database.

Usually ignored by Git.

### `chat_history.db`

SQLite chat history database.

Usually ignored by Git.

---

## API Endpoints

### Health

```text
GET /
```

Returns system configuration and health status.

---

### Admin Pages

```text
GET /app
GET /chat-demo
```

---

### Documents

```text
POST /documents/upload
GET /documents
DELETE /documents/{source}
```

---

### RAG

```text
POST /ask
POST /search
POST /debug
```

---

### Chat

```text
POST /chat
GET /chat/sessions
GET /chat/sessions/{session_id}
DELETE /chat/sessions/{session_id}
GET /chat/messages/recent
```

---

## Main Technologies

### FastAPI

Used for the backend API.

### Ollama

Runs the local LLM.

Current model:

```text
llama3.2:1b
```

### ChromaDB

Stores vector embeddings and retrieves relevant document chunks.

### SentenceTransformers

Creates embeddings for documents and questions.

Current embedding model:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

### SQLite

Stores persistent chat history.

### JavaScript

Used for the embeddable chatbot widget and admin dashboard.

---

## Environment Variables

Example `.env`:

```env
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3.2:1b

CHROMA_DIR=chroma_db
COLLECTION_NAME=consultation_knowledge
KNOWLEDGE_DIR=knowledge_base

EMBEDDING_MODEL_NAME=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

TOP_K=3
MAX_DISTANCE=20

CHAT_DB_PATH=chat_history.db
MAX_CHAT_MESSAGES=8
```

---

## Git Ignore Strategy

The following should not be committed:

```text
.env
venv/
__pycache__/
chat_history.db
chroma_db/
knowledge_base/
```

These are local runtime files, databases, uploaded documents, or environment-specific files.

---

## Current Limitations

This is still a learning project.

Current limitations:

* Only `.txt` file upload is supported
* No authentication for admin dashboard yet
* No user accounts
* No production deployment setup yet
* No Docker setup yet
* CORS allows all origins in learning mode
* Chat memory is stored locally in SQLite
* No streaming response yet
* No hybrid search yet
* No PDF ingestion yet

---

## Planned Improvements

Good next steps:

1. Add admin authentication
2. Add Docker and Docker Compose
3. Add PDF upload support
4. Add hybrid search
5. Add conversation summary memory
6. Add streaming chatbot responses
7. Add better Persian text normalization
8. Add production CORS configuration
9. Add rate limiting
10. Add PostgreSQL option
11. Add deployment guide
12. Add frontend theme customization for chatbot widget

---

## Portfolio Summary

This project demonstrates practical AI Engineering skills:

* Building an LLM-powered backend
* Implementing RAG with vector search
* Using local models with Ollama
* Creating embeddings with SentenceTransformers
* Persisting chat history with SQLite
* Designing backend guardrails
* Structuring a maintainable FastAPI project
* Building an embeddable chatbot widget
* Creating an admin dashboard
* Writing evaluation scripts for RAG quality

---

## Example Project Description

A local RAG-based AI consultation platform built with FastAPI, Ollama, ChromaDB, SentenceTransformers, and SQLite. The system supports document upload, vector search, AI question answering, backend guardrails, persistent chat memory, an admin dashboard, and an embeddable chatbot widget that can be added to any website.
