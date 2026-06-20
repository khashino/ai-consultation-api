# Local Setup Guide

This guide explains how to run the AI Consultation RAG Platform locally.

---

## Requirements

You need:

* Python 3.10+
* pip
* virtualenv or Python venv
* Ollama installed
* A local Ollama model pulled
* Linux, macOS, or Windows WSL

This project was developed on Linux.

---

## 1. Clone or Open the Project

Go to the project folder:

```bash
cd /app/projects/ai/ai-engineer-roadmap/ai-consultation-api
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

On Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

---

## 3. Install Requirements

```bash
pip install -r requirements.txt
```

Expected important packages:

```text
fastapi
uvicorn
pydantic
python-dotenv
requests
chromadb
sentence-transformers
python-multipart
```

---

## 4. Install and Run Ollama

Install Ollama from the official Ollama website if it is not installed.

Start Ollama:

```bash
ollama serve
```

In another terminal, pull the model:

```bash
ollama pull llama3.2:1b
```

Test it:

```bash
ollama run llama3.2:1b
```

---

## 5. Create `.env`

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

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

## 6. Start the API

Run:

```bash
uvicorn main:app --reload
```

The API should start at:

```text
http://127.0.0.1:8000
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

Open the admin dashboard:

```text
http://127.0.0.1:8000/app
```

Open the chatbot demo:

```text
http://127.0.0.1:8000/chat-demo
```

---

## 7. First Startup Notes

On first startup, the project may download the embedding model from Hugging Face:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

This may take time.

After the model is cached locally, startup becomes faster.

The project will also create:

```text
chat_history.db
chroma_db/
knowledge_base/
```

---

## 8. Upload Documents

Go to:

```text
http://127.0.0.1:8000/app
```

Open the Documents section.

Upload a UTF-8 `.txt` file.

The system will:

1. Save the file to `knowledge_base/`
2. Split it into chunks
3. Create embeddings
4. Store vectors in ChromaDB

---

## 9. Ask Questions

Use the admin dashboard:

```text
http://127.0.0.1:8000/app
```

Or call the API:

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Why are embeddings important for Persian RAG?",
    "topic": "AI",
    "user_country": null,
    "target_country": null
  }'
```

---

## 10. Test the Chatbot

Open:

```text
http://127.0.0.1:8000/chat-demo
```

Ask:

```text
Why are embeddings important for Persian RAG?
```

Then ask:

```text
Explain it simpler.
```

The chatbot should use previous chat history to understand what “it” means.

---

## 11. Test Persistent Memory

1. Open chatbot demo.
2. Ask a few questions.
3. Stop the server with `CTRL + C`.
4. Start it again:

```bash
uvicorn main:app --reload
```

5. Open the chatbot again.
6. Ask:

```text
What was my previous question about?
```

Because the browser keeps the same session ID in localStorage and the backend stores messages in SQLite, memory should still exist.

---

## 12. Admin Chat Sessions

Open:

```text
http://127.0.0.1:8000/app
```

Go to:

```text
Chat Sessions
```

You can:

* See all sessions
* Click a session
* View full question and answer history
* Delete a session
* Refresh session history

---

## 13. Useful API Endpoints

### Health

```text
GET /
```

### Admin dashboard

```text
GET /app
```

### Chatbot demo

```text
GET /chat-demo
```

### Upload document

```text
POST /documents/upload
```

### List documents

```text
GET /documents
```

### Delete document

```text
DELETE /documents/{source}
```

### Ask RAG

```text
POST /ask
```

### Search knowledge base

```text
POST /search
```

### Debug RAG prompt

```text
POST /debug
```

### Chatbot

```text
POST /chat
```

### List chat sessions

```text
GET /chat/sessions
```

### Get one session

```text
GET /chat/sessions/{session_id}
```

### Delete one session

```text
DELETE /chat/sessions/{session_id}
```

### Recent messages

```text
GET /chat/messages/recent
```

---

## 14. Run Scripts

Make sure the API is running for API scripts:

```bash
uvicorn main:app --reload
```

In another terminal:

```bash
python scripts/test_api.py
python scripts/evaluate_api.py
```

Scripts that use local services directly:

```bash
python scripts/test_retrieval.py
python scripts/evaluate_retrieval.py
python scripts/ingest_documents.py
```

---

## 15. Common Problems

### Problem: Ollama connection error

Check Ollama is running:

```bash
ollama serve
```

Check model exists:

```bash
ollama list
```

Pull model again if needed:

```bash
ollama pull llama3.2:1b
```

---

### Problem: `python-multipart` missing

Install requirements again:

```bash
pip install -r requirements.txt
```

Or install directly:

```bash
pip install python-multipart
```

This package is needed for file uploads.

---

### Problem: ChromaDB has old or wrong documents

Delete local vector DB:

```bash
rm -rf chroma_db
```

Then restart the API and upload or re-ingest documents again.

---

### Problem: Chat history is wrong or too old

Delete SQLite database:

```bash
rm chat_history.db
```

Then restart:

```bash
uvicorn main:app --reload
```

Or delete individual sessions from the admin dashboard.

---

### Problem: Admin dashboard not updating

Hard refresh the browser:

```text
CTRL + F5
```

Or clear browser cache.

---

## 16. Recommended Development Workflow

Start Ollama:

```bash
ollama serve
```

Start API:

```bash
source venv/bin/activate
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000/app
```

Use scripts to test:

```bash
python scripts/test_api.py
python scripts/evaluate_retrieval.py
```

Commit code changes, but do not commit:

```text
.env
venv/
chat_history.db
chroma_db/
knowledge_base/
```

---

## 17. Current Local Files Created at Runtime

These are local runtime files:

```text
chat_history.db
chroma_db/
knowledge_base/
__pycache__/
```

They are ignored by Git.

---

## 18. Next Recommended Improvements

After local setup works, continue with:

1. Admin login
2. Docker setup
3. PDF upload
4. Hybrid search
5. Chat streaming
6. Production CORS
7. Better frontend styling
8. Deployment guide
