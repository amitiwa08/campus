"""
Routes for AI endpoints.
AI Developer 2: categorise, query, health, generate-report
"""

import logging
from flask import Blueprint, request, jsonify
from services.groq_client import GroqClient
from services.chroma_client import ChromaClient
from services.cache_manager import CacheManager
import json
import os
from datetime import datetime

# Initialize
ai_bp = Blueprint("ai", __name__, url_prefix="/api/ai")
logger = logging.getLogger(__name__)

groq_client = None
chroma_client = None
cache_manager = None


def init_clients():
    """Initialize AI service clients."""
    global groq_client, chroma_client, cache_manager

    groq_client = GroqClient(api_key=os.getenv("GROQ_API_KEY"))
    chroma_client = ChromaClient(persist_dir=os.getenv("CHROMA_DATA_DIR", "./chroma_data"))
    cache_manager = CacheManager(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
    )

    # Seed ChromaDB
    chroma_client.seed_documents()
    logger.info("AI clients initialized")


@ai_bp.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint with AI service metrics.
    Day 7: AI Developer 2
    """
    doc_count = chroma_client.get_doc_count() if chroma_client else 0
    cache_stats = cache_manager.get_stats() if cache_manager else {}

    return jsonify(
        {
            "status": "healthy",
            "model": "llama-3.3-70b-versatile",
            "last_response_time_ms": (
                groq_client.get_last_response_time() * 1000 if groq_client else 0
            ),
            "chroma_doc_count": doc_count,
            "cache_stats": cache_stats,
            "uptime_minutes": (datetime.utcnow() - datetime(2026, 5, 2)).total_seconds()
            / 60,
        }
    ),  200


@ai_bp.route("/categorise", methods=["POST"])
def categorise():
    """
    Classify compliance training content into categories.
    Day 3: AI Developer 2
    Caching: Day 8
    """
    try:
        data = request.get_json()
        content = data.get("content", "").strip()

        if not content:
            return jsonify({"error": "Content is required"}), 400

        # Check cache
        cache_key = {"endpoint": "categorise", "content": content}
        cached = cache_manager.get("categorise", cache_key)
        if cached:
            cached["meta"]["cached"] = True
            return jsonify(cached), 200

        # Load prompt
        with open("prompts/categorise.txt", "r") as f:
            prompt_template = f.read()

        prompt = prompt_template.format(content=content)

        # Call Groq
        groq_response = groq_client.call(
            prompt=prompt,
            temperature=0.3,
            max_tokens=300,
            system_message="You are a compliance categorization expert. Respond only with valid JSON.",
        )

        if not groq_response["success"]:
            return jsonify(
                {
                    "error": groq_response["error"],
                    "meta": {
                        "confidence": 0.0,
                        "model_used": groq_client.model,
                        "cached": False,
                        "is_fallback": True,
                    },
                }
            ), 503

        # Parse JSON
        response_json = groq_client.parse_json_response(groq_response["content"])
        if not response_json:
            return jsonify({"error": "Failed to parse response"}), 500

        result = {
            **response_json,
            "meta": {
                "confidence": response_json.get("confidence", 0.0),
                "model_used": groq_client.model,
                "tokens_used": groq_response["tokens_used"],
                "response_time_ms": groq_response["response_time_ms"],
                "cached": False,
                "is_fallback": groq_response["is_fallback"],
            },
        }

        # Cache result
        cache_manager.set("categorise", cache_key, result)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Categorise error: {e}")
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/query", methods=["POST"])
def query():
    """
    RAG-powered query endpoint with ChromaDB semantic search.
    Day 5: AI Developer 2
    """
    try:
        data = request.get_json()
        question = data.get("question", "").strip()

        if not question:
            return jsonify({"error": "Question is required"}), 400

        # Query ChromaDB
        chroma_results = chroma_client.query(question, top_k=3)

        if not chroma_results["success"]:
            return jsonify({"error": "Search failed"}), 500

        # Build context from top results
        context = "\n".join([r["text"] for r in chroma_results["results"]])

        # Call Groq with context
        prompt = f"""Based on the following compliance training context, answer this question:

Context:
{context}

Question: {question}

Provide a clear, accurate answer based only on the context provided."""

        groq_response = groq_client.call(
            prompt=prompt,
            temperature=0.3,
            max_tokens=500,
            system_message="You are a compliance training assistant. Answer questions based on provided context.",
        )

        if not groq_response["success"]:
            return jsonify({"error": groq_response["error"]}), 503

        result = {
            "answer": groq_response["content"],
            "sources": [
                {
                    "text": r["text"][:200],
                    "distance": r["distance"],
                    "metadata": r["metadata"],
                }
                for r in chroma_results["results"]
            ],
            "meta": {
                "model_used": groq_client.model,
                "tokens_used": groq_response["tokens_used"],
                "response_time_ms": groq_response["response_time_ms"],
                "cached": False,
                "is_fallback": groq_response["is_fallback"],
            },
        }

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Query error: {e}")
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/generate-report", methods=["POST"])
def generate_report():
    """
    Generate comprehensive compliance report.
    Day 11: AI Developer 2 (async job processing)
    """
    try:
        data = request.get_json()
        topic = data.get("topic", "").strip()
        department = data.get("department", "General").strip()
        context = data.get("context", "").strip()

        if not topic:
            return jsonify({"error": "Topic is required"}), 400

        # Check cache
        cache_key = {"endpoint": "generate-report", "topic": topic, "department": department}
        cached = cache_manager.get("generate-report", cache_key)
        if cached and not data.get("fresh"):
            cached["meta"]["cached"] = True
            return jsonify(cached), 200

        # Load prompt
        with open("prompts/generate_report.txt", "r") as f:
            prompt_template = f.read()

        prompt = prompt_template.format(topic=topic, department=department, context=context)

        # Call Groq
        groq_response = groq_client.call(
            prompt=prompt,
            temperature=0.4,
            max_tokens=2000,
            system_message="You are a compliance training expert. Generate professional, accurate reports.",
        )

        if not groq_response["success"]:
            return jsonify({"error": groq_response["error"]}), 503

        # Parse JSON
        response_json = groq_client.parse_json_response(groq_response["content"])
        if not response_json:
            return jsonify({"error": "Failed to parse report"}), 500

        result = {
            **response_json,
            "meta": {
                "confidence": 0.85,
                "model_used": groq_client.model,
                "tokens_used": groq_response["tokens_used"],
                "response_time_ms": groq_response["response_time_ms"],
                "cached": False,
                "is_fallback": groq_response["is_fallback"],
            },
        }

        # Cache result
        cache_manager.set("generate-report", cache_key, result, ttl=1800)  # 30 min

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Generate report error: {e}")
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/batch-process", methods=["POST"])
def batch_process():
    """
    Process multiple items in batch.
    Day 11: AI Developer 1
    """
    try:
        data = request.get_json()
        items = data.get("items", [])

        if not items or len(items) > 20:
            return jsonify({"error": "Provide 1-20 items"}), 400

        results = []
        for item in items:
            # Process each item (simplified for demo)
            result = {
                "item": item,
                "status": "processed",
                "classification": "General Compliance",
            }
            results.append(result)

        return jsonify({"results": results, "processed": len(results)}), 200

    except Exception as e:
        logger.error(f"Batch process error: {e}")
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/cache-stats", methods=["GET"])
def cache_stats():
    """Get cache statistics."""
    return jsonify(cache_manager.get_stats()), 200
