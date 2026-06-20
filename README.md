# AI Consultation API

A local AI/RAG platform built with FastAPI, Ollama, ChromaDB, SentenceTransformers, and SQLite.

This project started as a learning project for practical AI Engineering and evolved into a small local AI platform with:

* Local Ollama LLM integration
* RAG using ChromaDB
* SentenceTransformers embeddings
* SQLite chat memory
* Admin dashboard
* Full ChatGPT-style local chat page
* Embeddable chatbot widget for websites
* Document upload and vector search
* Admin login/logout
* Runtime Ollama model switching

The goal is to provide a simple, practical starting point for building local AI applications without depending on external LLM APIs.

---

## Project Repository

```text
https://github.com/khashino/ai-consultation-api.git
```

---

## Features

### Local RAG System

Upload `.txt` documents, chunk them, embed them, and store them in ChromaDB. The assistant retrieves relevant context before answering.

### Local LLM with Ollama

The project uses Ollama to run local models such as:

```text
llama3.2:1b
```

You can switch between installed Ollama models from the admin dashboard.

### Admin Dashboard

Protected admin dashboard for:

* Viewing system status
* Uploading documents
* Listing indexed documents
* Deleting documents
* Testing RAG answers
* Debugging retrieval and prompts
* Viewing chat sessions
* Viewing recent messages
* Switching Ollama models

### Full Chat App

A ChatGPT-style local chat page with:

* New chat
* Historical sessions
* Chat memory
* Sidebar history
* Local RAG answers

### Embeddable Chatbot Widget

A lightweight website widget that can be embedded into any HTML page.

It calls the public `/chat` endpoint and answers using your local knowledge base.

---

## Tech Stack

* Python
* FastAPI
* Uvicorn
* Ollama
* ChromaDB
* SentenceTransformers
* SQLite
* HTML
* CSS
* JavaScript

---

## Requirements

Before running this project, install:

* Python 3.10+
* Ollama
* Git

Recommended Python version:

```text
Python 3.10 or 3.11
```

Python 3.13 may work, but some AI/ML packages can be more stable on Python 3.10 or 3.11.

---

# 1. Install Ollama First

This project uses Ollama for the local LLM.

Install Ollama from:

```text
https://ollama.com
```

After installation, check that Ollama works:

```bash
ollama --version
```

Start Ollama if it is not already running:

```bash
ollama serve
```

In another terminal, pull a model:

```bash
ollama pull llama3.2:1b
```

You can check installed models with:

```bash
ollama list
```

---

# 2. Clone the Project

```bash
git clone https://github.com/khashino/ai-consultation-api.git
cd ai-consultation-api
```

---

# 3. Create a Virtual Environment

Linux/macOS:

```bash
python -m venv venv
source venv/bin/activate
```

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

---

# 4. Install Dependencies

```bash
pip install -r requirements.txt
```

If `python-multipart` is missing, install it manually:

```bash
pip install python-multipart
```

This is needed for file upload and login form handling.

---

# 5. Create `.env`

Copy the example environment file:

```bash
cp .env.example .env
```

On Windows:

```bash
copy .env.example .env
```

Then edit `.env`.

Example:

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

ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-this-password

ADMIN_SESSION_SECRET=change-this-to-a-long-random-secret
ADMIN_COOKIE_NAME=admin_session
ADMIN_COOKIE_SECURE=false

RUNTIME_CONFIG_PATH=runtime_config.json
```

Generate a secure session secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Use the generated value for:

```env
ADMIN_SESSION_SECRET=
```

Do not commit `.env` to GitHub.

---

# 6. Run the API

Make sure Ollama is running first.

Then start FastAPI:

```bash
uvicorn main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

---

## Main Pages

### Admin Dashboard

```text
http://127.0.0.1:8000/app
```

This page is protected by login.

Use the admin credentials from your `.env` file:

```text
ADMIN_USERNAME
ADMIN_PASSWORD
```

### Full Chat App

```text
http://127.0.0.1:8000/chat-app
```

This is a ChatGPT-style local chat interface with historical sessions.

### Embeddable Chatbot Demo

```text
http://127.0.0.1:8000/chat-demo
```

This page demonstrates the website chatbot widget.

### API Docs

```text
http://127.0.0.1:8000/docs
```

---

## Basic Usage

### 1. Login to Admin

Open:

```text
http://127.0.0.1:8000/app
```

Login using the credentials from `.env`.

### 2. Upload Documents

Go to the Documents section and upload `.txt` files.

The system will:

1. Save the document
2. Split it into chunks
3. Generate embeddings
4. Store chunks in ChromaDB

### 3. Ask Questions

Use either:

```text
/app
```

or:

```text
/chat-app
```

The assistant will retrieve relevant document chunks and answer using the local Ollama model.

### 4. Use the Website Widget

Open:

```text
http://127.0.0.1:8000/chat-demo
```

Or embed the widget in your own HTML page:

```html
<script>
  window.AI_CHATBOT_API_BASE = "http://127.0.0.1:8000";
  window.AI_CHATBOT_TITLE = "RAG Assistant";
  window.AI_CHATBOT_SUBTITLE = "Answers from the local knowledge base";
  window.AI_CHATBOT_TOPIC = "general";
  window.AI_CHATBOT_USER_COUNTRY = null;
  window.AI_CHATBOT_TARGET_COUNTRY = null;
</script>

<script src="http://127.0.0.1:8000/static/chatbot-widget.js"></script>
```

---

## API Endpoints

### Public Endpoints

```text
GET  /
GET  /chat-demo
POST /chat
POST /ask
POST /search
```

### Admin Pages

```text
GET  /login
POST /login
POST /logout
GET  /app
GET  /chat-app
```

### Admin Document Endpoints

```text
POST   /documents/upload
GET    /documents
DELETE /documents/{source}
```

### Admin Chat History Endpoints

```text
GET    /chat/sessions
GET    /chat/sessions/{session_id}
DELETE /chat/sessions/{session_id}
GET    /chat/messages/recent
```

### Admin Model Endpoints

```text
GET  /admin/models
POST /admin/model
```

### Admin Debug Endpoint

```text
POST /debug
```

---

## Example Chat Request

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session",
    "message": "What should I check first?",
    "topic": "general",
    "user_country": null,
    "target_country": null
  }'
```

---

## Example Ask Request

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What should I check for a Germany work visa?",
    "topic": "immigration",
    "user_country": "Iran",
    "target_country": "Germany"
  }'
```

---

## Runtime Files

The following files and folders are generated locally and should not be committed:

```text
.env
chat_history.db
runtime_config.json
chroma_db/
knowledge_base/
__pycache__/
venv/
```

Make sure your `.gitignore` includes them.

---

## Recommended `.gitignore`

```gitignore
__pycache__/
*.py[cod]

venv/
.venv/
env/

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
chat_history.db
runtime_config.json

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

outputs/
tmp/
temp/

node_modules/
dist/
build/
```

---

## Project Structure

```text
ai-consultation-api/
├── app/
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── models/
│   │   └── schemas.py
│   ├── repositories/
│   │   └── chat_repository.py
│   ├── routers/
│   │   ├── admin.py
│   │   ├── chat.py
│   │   ├── documents.py
│   │   ├── health.py
│   │   ├── pages.py
│   │   └── rag.py
│   ├── services/
│   │   ├── chat_service.py
│   │   ├── document_service.py
│   │   ├── embedding_service.py
│   │   ├── guardrail_service.py
│   │   ├── ollama_service.py
│   │   ├── rag_service.py
│   │   └── vector_store_service.py
│   ├── dependencies.py
│   └── main.py
├── scripts/
├── static/
│   ├── index.html
│   ├── chat.html
│   ├── embed-demo.html
│   └── chatbot-widget.js
├── .env.example
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

---

## Notes About Local Models

This project does not include Ollama models in the repository.

Each user should install Ollama and pull the model locally:

```bash
ollama pull llama3.2:1b
```

You can also try other installed models:

```bash
ollama pull llama3.2:3b
ollama pull qwen2.5:0.5b
```

Then switch models from the admin dashboard.

---

## Troubleshooting

### Ollama connection error

Make sure Ollama is running:

```bash
ollama serve
```

Check installed models:

```bash
ollama list
```

### Model not found

Pull the model:

```bash
ollama pull llama3.2:1b
```

Make sure `.env` uses the same model name:

```env
OLLAMA_MODEL=llama3.2:1b
```

### Login form error

Make sure `python-multipart` is installed:

```bash
pip install python-multipart
```

### No answers from documents

Upload at least one `.txt` document from the admin dashboard.

Then ask a question related to the document content.

### Hugging Face warning

You may see a warning about unauthenticated Hugging Face downloads.

For local development, this is usually okay.

To avoid rate limits, you can set a Hugging Face token if needed.

---

## Current Limitations

* Only `.txt` upload is supported
* No PDF extraction yet
* No Docker setup yet
* No streaming responses yet
* No multi-user admin roles yet
* Public chatbot endpoint is intentionally open for embedding

---

## Future Improvements

Possible next improvements:

* PDF upload support
* Docker and Docker Compose
* Streaming chat responses
* Persian text normalization
* Hybrid search with BM25
* Better evaluation scripts
* Conversation summary memory
* Multi-user admin accounts

---

## License

This project is open for learning, experimentation, and portfolio use.

Add your preferred license file if you plan to distribute it more formally.
