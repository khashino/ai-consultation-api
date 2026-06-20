# AI Consultation API

A local AI Engineering project built with FastAPI, Ollama, ChromaDB, embeddings, and RAG.

This project demonstrates how to build a practical backend AI system that can:

- Accept user questions through an API
- Retrieve relevant context from a local knowledge base
- Use a local LLM through Ollama
- Return structured JSON responses
- Apply backend safety guardrails
- Upload, list, search, and delete documents
- Support Persian and English knowledge documents

## Why this project exists

The goal of this project is to learn practical AI Engineering.

Instead of only sending prompts to an LLM, this project treats the LLM as one component inside a backend system.

The system includes:

- API design
- Document ingestion
- Text chunking
- Embeddings
- Vector search
- RAG
- Structured output validation
- Guardrails
- Retrieval debugging
- Document management

## Architecture

User Question
    ↓
FastAPI Endpoint
    ↓
Embedding Model
    ↓
ChromaDB Vector Search
    ↓
Retrieved Context
    ↓
Prompt Builder
    ↓
Ollama Local LLM
    ↓
JSON Parsing
    ↓
Pydantic Validation
    ↓
Backend Guardrails
    ↓
Structured API Response

## Tech Stack

- Python
- FastAPI
- Ollama
- llama3.2:1b
- ChromaDB
- Sentence Transformers
- paraphrase-multilingual-MiniLM-L12-v2
- Pydantic
- Uvicorn

## Main Features

### Ask a question

POST /ask

Uses RAG to answer a user question based on local documents.

### Search knowledge base

POST /search

Searches ChromaDB and returns retrieved chunks without calling the LLM.

Useful for debugging retrieval quality.

### Debug response

POST /debug

Shows:

- Retrieved context
- Prompt
- Raw model output
- Parsed output

### Upload document

POST /documents/upload

Uploads a .txt document, chunks it, embeds it, and stores it in ChromaDB.

### List documents

GET /documents

Lists documents currently stored in the vector database.

### Delete document

DELETE /documents/{source}

Deletes all chunks for a document and removes the local file.

## Example request

{
  "question": "What should I check for a Germany work visa?",
  "topic": "immigration",
  "user_country": "Iran",
  "target_country": "Germany"
}

## Example response

{
  "answer": "A person who wants to work in Germany usually needs to check the correct visa or residence permit category. Important factors may include a valid job offer, relevant education or professional qualification, and salary requirements depending on the visa type.",
  "confidence": "medium",
  "needs_human_review": true,
  "suggested_next_steps": [
    "check official German immigration rules",
    "review qualifications with a qualified expert",
    "consider job offers from reputable employers"
  ],
  "sources": [
    "germany_work_visa.txt"
  ]
}

## Important AI Engineering Lessons

### 1. Valid JSON does not mean valid AI behavior

The model can return valid JSON but still produce unsafe or overconfident answers.

That is why this project uses backend guardrails after the LLM response.

### 2. Prompts are not enough

Prompts guide the model, but backend rules protect the product.

Sensitive topics such as immigration, legal, medical, and financial questions require deterministic safety checks.

### 3. Retrieval quality matters

In RAG systems, bad retrieval leads to bad answers.

This project includes /search and /debug endpoints to inspect retrieval quality before blaming the LLM.

### 4. The LLM is not the application

The real application is the system around the LLM:

- validation
- retrieval
- guardrails
- logging
- fallbacks
- document management
- API design

## Running the project

Create virtual environment:

python3 -m venv venv
source venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Start Ollama:

sudo systemctl start ollama

Pull model:

ollama pull llama3.2:1b

Run API:

uvicorn main:app --reload

Open API docs:

http://127.0.0.1:8000/docs

## Environment variables

Create .env:

OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3.2:1b

CHROMA_DIR=chroma_db
COLLECTION_NAME=consultation_knowledge
KNOWLEDGE_DIR=knowledge_base

EMBEDDING_MODEL_NAME=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

TOP_K=3
MAX_DISTANCE=20

## Status

Version: 1.0

This is a learning project for practical AI Engineering, focused on local LLMs, RAG, embeddings, vector databases, backend guardrails, and enterprise-style API design.