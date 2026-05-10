# CampusPe AI Service Documentation

## Overview
The CampusPe AI Service is a high-performance microservice designed to handle compliance training tasks, automated reporting, and semantic document querying. It leverages the **Groq Llama 3.3 70B** model for near-instant inference and **ChromaDB** for vector-based Retrieval Augmented Generation (RAG).

## Core Components

### 1. GroqClient (`services/groq_client.py`)
- **Model**: `llama-3.3-70b-versatile`
- **Features**:
  - Exponential backoff retry logic.
  - Robust JSON parsing (handles markdown extraction).
  - Performance monitoring (latency tracking).

### 2. /generate-report Endpoint
- **Method**: `POST /api/ai/generate-report`
- **Purpose**: Generates structured JSON reports for compliance topics.
- **Payload**:
  ```json
  {
    "topic": "Data Privacy",
    "department": "Engineering",
    "context": "Focus on GDPR and CCPA"
  }
  ```
- **Caching**: Results are cached for 30 minutes via Redis.

### 3. /query Endpoint (RAG)
- **Method**: `POST /api/ai/query`
- **Purpose**: Semantic search across uploaded compliance documents.
- **Workflow**:
  1. Embed query.
  2. Search ChromaDB.
  3. Inject context into Groq prompt.
  4. Return sourced answer.

## Security Features
- **Environment Isolation**: API keys managed via `.env`.
- **Input Sanitization**: Basic stripping and length checks.
- **Error Masking**: User-friendly errors instead of stack traces in production.

## Maintenance
- **Logs**: Located in standard output (standard Flask logging).
- **Health Checks**: `/api/ai/health` provides real-time metrics on ChromaDB and Groq latency.
