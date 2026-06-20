# Project Context for Next Chat

Use this document to continue the project in another ChatGPT conversation.

---

## Project Name

AI Consultation RAG Platform

---

## User Goal

The user is learning practical AI Engineering by building a real portfolio project.

The project is a local RAG-based AI consultation platform with:

* FastAPI backend
* Ollama local LLM
* ChromaDB vector database
* SentenceTransformers embeddings
* SQLite chat memory
* Admin dashboard
* Embeddable chatbot widget
* Document upload
* Backend guardrails
* Evaluation scripts

The user prefers step-by-step, hands-on guidance with complete code when needed.

---

## User Background

The user has backend, enterprise integration, Oracle/APEX, telecom, and presales experience.

They are positioning themselves toward roles like:

* Backend AI Engineer
* AI Engineer
* LLM Application Developer
* RAG Developer
* AI Automation Engineer
* Enterprise AI Solutions Engineer

They want practical, portfolio-ready AI Engineering skills.

---

## Current Project Path

The project is located at:

```text
/app/projects/ai/ai-engineer-roadmap/ai-consultation-api
```

---

## Current Local Structure

Expected current structure:

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

Root `main.py` should only contain:

```python
from app.main import app
```

---

## Current `.env`

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

## Current Main Technologies

* Python
* FastAPI
* Uvicorn
* Ollama
* ChromaDB
* SentenceTransformers
* SQLite
* Pydantic
* JavaScript
* HTML/CSS

---

## Current Ollama Model

```text
llama3.2:1b
```

The user chose a local Ollama model instead of OpenAI/Gemini.

---

## Current Embedding Model

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Chosen because the project includes multilingual and Persian RAG testing.

---

## Current Runtime Files

These exist locally and should usually be ignored by Git:

```text
chat_history.db
chroma_db/
knowledge_base/
venv/
__pycache__/
```

---

## Current API Endpoints

### Health

```text
GET /
```

### Pages

```text
GET /app
GET /chat-demo
```

### Documents

```text
POST /documents/upload
GET /documents
DELETE /documents/{source}
```

### RAG

```text
POST /ask
POST /search
POST /debug
```

### Chat

```text
POST /chat
GET /chat/sessions
GET /chat/sessions/{session_id}
DELETE /chat/sessions/{session_id}
GET /chat/messages/recent
```

---

## Current Frontend

### Admin Dashboard

URL:

```text
http://127.0.0.1:8000/app
```

Current admin dashboard features:

* Dashboard metrics
* System info
* Document upload
* Document list
* Document deletion
* Ask RAG API
* Debug RAG request
* Search knowledge base
* Chat session list
* Click session to view full question/answer history
* Delete chat session
* Recent messages view

### Chatbot Demo

URL:

```text
http://127.0.0.1:8000/chat-demo
```

### Embeddable Chatbot

File:

```text
static/chatbot-widget.js
```

The widget:

* Creates a floating chat button
* Stores a session ID in localStorage
* Calls `POST /chat`
* Displays only the answer
* Has a “New” button to create a new session
* Can be embedded in any HTML page with a script tag

---

## Important Architecture Concepts Already Covered

### RAG Context vs Chat Memory

RAG context:

```text
Information retrieved from uploaded documents in ChromaDB
```

Chat memory:

```text
Previous user and assistant messages stored in SQLite
```

Both are used in `/chat`.

---

## Current RAG Flow

```text
Question
↓
SentenceTransformer embedding
↓
ChromaDB vector search
↓
Retrieved chunks
↓
Prompt
↓
Ollama
↓
JSON response
↓
Pydantic validation
↓
Guardrails
↓
Final API response
```

---

## Current Chat Flow

```text
Chat widget message
↓
session_id + message sent to /chat
↓
Recent chat history loaded from SQLite
↓
Relevant context retrieved from ChromaDB
↓
Prompt combines context + history + latest message
↓
Ollama returns JSON
↓
Assistant answer saved to SQLite
↓
Answer returned to widget
```

---

## Current Services After Refactor

### `EmbeddingService`

Loads SentenceTransformer and creates embeddings.

### `VectorStoreService`

Handles ChromaDB:

* Upsert chunks
* Search
* List documents
* Delete document

### `DocumentService`

Handles:

* Upload file
* Validate `.txt`
* Save file
* Chunk text
* Ingest chunks into vector store
* Delete local document file

### `OllamaService`

Handles:

* Calling Ollama API
* Requesting JSON output
* Extracting JSON from model response

### `RagService`

Handles:

* Building RAG prompt
* Calling Ollama
* Validating model response
* Applying guardrails
* Debugging prompts

### `ChatService`

Handles:

* Chat prompt
* Chat memory retrieval
* Saving user/assistant messages
* Listing sessions
* Getting session history
* Deleting sessions
* Recent messages

### `GuardrailService`

Handles:

* Cleaning invalid model sources
* Replacing placeholder next steps
* Lowering confidence for sensitive topics

### `ChatRepository`

Handles SQLite access.

---

## Important User Preferences

The user likes:

* Complete code
* Practical explanations
* Step-by-step guidance
* Portfolio-focused improvements
* Simple but production-inspired architecture
* Friendly, direct explanations
* Learning by building

Avoid giving only abstract advice. Prefer implementation.

---

## Current Git Ignore Strategy

`.gitignore` should ignore:

```gitignore
__pycache__/
*.py[cod]
venv/
.venv/
.env
.env.*
!.env.example
*.log
.vscode/
.idea/
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.db
*.sqlite
*.sqlite3
chroma_db/
knowledge_base/
.cache/
models/
hf_cache/
sentence_transformers/
*.safetensors
*.bin
*.pt
*.onnx
main_old.py
outputs/
tmp/
temp/
node_modules/
dist/
build/
scripts/*.log
scripts/output/
scripts/outputs/
```

---

## Current Scripts

Scripts are in:

```text
scripts/
```

Current scripts:

```text
scripts/test_api.py
scripts/test_retrieval.py
scripts/evaluate_api.py
scripts/evaluate_retrieval.py
scripts/ingest_documents.py
```

Some scripts call the running API. Some use services directly.

---

## Current Status

The user has successfully built and tested:

* FastAPI backend
* Ollama integration
* Structured JSON generation
* Guardrails
* ChromaDB RAG
* Document upload/list/delete
* Admin dashboard
* Embeddable chatbot
* Session memory
* SQLite persistent chat history
* Admin chat session viewer
* Project modular refactor
* Scripts folder cleanup

---

## Recommended Next Steps

Good next steps from here:

### 1. Add Admin Authentication

Protect `/app` and admin APIs.

Options:

* Simple username/password from `.env`
* HTTP Basic Auth
* Login form with session cookie
* JWT later

Recommended first step:

```text
Simple HTTP Basic Auth for admin routes
```

### 2. Add Docker

Create:

```text
Dockerfile
docker-compose.yml
```

Potential challenge:

Ollama can run outside Docker first. Keep Docker simple initially.

### 3. Add PDF Upload

Add support for:

```text
.pdf
```

Use a PDF text extraction package such as PyMuPDF.

Flow:

```text
Upload PDF
↓
Extract text
↓
Chunk text
↓
Embed chunks
↓
Store in ChromaDB
```

### 4. Add Persian Text Normalization

Before embedding:

* Normalize Arabic `ي` to Persian `ی`
* Normalize Arabic `ك` to Persian `ک`
* Normalize whitespace
* Handle half-space carefully

Apply normalization both during ingestion and query embedding.

### 5. Add Hybrid Search

Combine:

* Vector search
* Keyword search
* Maybe BM25

This improves retrieval for exact technical terms, company names, document numbers, and mixed Persian/English content.

### 6. Add Streaming Chat Responses

Current chatbot waits for the full answer.

Later add streaming:

* Backend streaming endpoint
* Frontend incremental rendering

### 7. Add Conversation Summary Memory

Current memory uses recent messages only.

Later:

* Summarize older messages
* Keep short summary per session
* Combine summary + recent turns

### 8. Add Tests with Pytest

Current scripts are manual.

Later add:

```text
tests/
```

With pytest test files.

### 9. Add Better README Screenshots

Take screenshots of:

* Admin dashboard
* Documents page
* Chat sessions page
* Chatbot widget
* API docs

### 10. Prepare LinkedIn Post

Possible post topic:

```text
I started with one main.py file, then refactored my RAG project into routers, services, repositories, schemas, and config.
```

Lesson:

```text
AI Engineering is still software engineering.
The model is only one part of the product.
```

---

## Suggested Immediate Next Task

The best next task is:

```text
Add simple admin authentication
```

Reason:

The admin dashboard can view chat history and delete documents/sessions. In a real product, this should not be public.

Recommended implementation:

* Add `ADMIN_USERNAME` and `ADMIN_PASSWORD` to `.env`
* Create `app/core/security.py`
* Use FastAPI `HTTPBasic`
* Protect `/app`
* Protect document and chat session admin endpoints
* Keep public `/chat` available for embedded widget

Important distinction:

Public endpoints:

```text
GET /
GET /chat-demo
POST /chat
```

Admin endpoints should be protected:

```text
GET /app
POST /documents/upload
GET /documents
DELETE /documents/{source}
GET /chat/sessions
GET /chat/sessions/{session_id}
DELETE /chat/sessions/{session_id}
GET /chat/messages/recent
POST /debug
```

Potentially `/ask` and `/search` can stay public or become admin-only depending on use case.

---

## Prompt for Next Chat

Continue this project from here. The project is a local FastAPI RAG platform with Ollama, ChromaDB, SentenceTransformers, SQLite chat memory, an admin dashboard, and embeddable chatbot. It has already been refactored into routers, services, repositories, schemas, and config. The next best improvement is simple admin authentication while keeping the public chatbot endpoint available.
