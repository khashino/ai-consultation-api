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

```text
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