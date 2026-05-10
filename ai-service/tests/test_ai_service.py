"""
Pytest unit tests for AI service.
AI Developer 2: Day 10 requirement
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from services.groq_client import GroqClient
from services.cache_manager import CacheManager


class TestGroqClient:
    """Test Groq client with mocked API."""

    @pytest.fixture
    def groq_client(self):
        return GroqClient(api_key="test-key", max_retries=2)

    def test_groq_successful_call(self, groq_client):
        """Test successful Groq API call."""
        with patch("services.groq_client.Groq") as mock_groq:
            # Mock response
            mock_response = MagicMock()
            mock_response.choices[0].message.content = '{"category": "Security", "confidence": 0.95}'
            mock_response.usage.total_tokens = 50

            mock_groq.return_value.chat.completions.create.return_value = mock_response

            groq_client.client = mock_groq.return_value

            result = groq_client.call(prompt="Test prompt")

            assert result["success"] is True
            assert "Security" in result["content"]
            assert result["tokens_used"] == 50

    def test_groq_fallback_on_error(self, groq_client):
        """Test fallback response on API error."""
        with patch("services.groq_client.Groq") as mock_groq:
            mock_groq.return_value.chat.completions.create.side_effect = Exception("API Error")

            groq_client.client = mock_groq.return_value

            result = groq_client.call(prompt="Test prompt")

            assert result["success"] is False
            assert result["is_fallback"] is True

    def test_json_parsing_from_markdown(self, groq_client):
        """Test JSON extraction from markdown code blocks."""
        markdown_json = '```json\n{"category": "Test"}\n```'
        parsed = groq_client.parse_json_response(markdown_json)

        assert parsed is not None
        assert parsed["category"] == "Test"

    def test_json_parsing_direct(self, groq_client):
        """Test direct JSON parsing."""
        json_str = '{"category": "Test", "confidence": 0.9}'
        parsed = groq_client.parse_json_response(json_str)

        assert parsed is not None
        assert parsed["confidence"] == 0.9


class TestCacheManager:
    """Test Redis cache manager."""

    @pytest.fixture
    def cache_manager(self):
        # Use mock Redis
        with patch("services.cache_manager.redis.Redis"):
            return CacheManager(host="localhost", port=6379)

    def test_cache_key_generation(self, cache_manager):
        """Test SHA256 key generation."""
        key1 = cache_manager._generate_key("test", {"a": 1})
        key2 = cache_manager._generate_key("test", {"a": 1})

        assert key1 == key2  # Same input = same key
        assert len(key1) == 64  # SHA256 = 64 hex chars

    def test_cache_get_miss(self, cache_manager):
        """Test cache miss."""
        cache_manager.redis_client = MagicMock()
        cache_manager.redis_client.get.return_value = None

        result = cache_manager.get("endpoint", {"param": "value"})

        assert result is None
        assert cache_manager.misses == 1

    def test_cache_set_get(self, cache_manager):
        """Test cache set and get."""
        cache_manager.redis_client = MagicMock()

        # Test set
        success = cache_manager.set("endpoint", {"param": "value"}, {"result": "data"})
        assert success is True

        # Test get
        cache_manager.redis_client.get.return_value = '{"result": "data"}'
        result = cache_manager.get("endpoint", {"param": "value"})

        assert result == {"result": "data"}

    def test_cache_stats(self, cache_manager):
        """Test cache statistics."""
        cache_manager.hits = 10
        cache_manager.misses = 5

        stats = cache_manager.get_stats()

        assert stats["hits"] == 10
        assert stats["misses"] == 5
        assert stats["total_requests"] == 15
        assert "66.7%" in stats["hit_rate"]


class TestEndpoints:
    """Test Flask endpoints (integration)."""

    @pytest.fixture
    def client(self):
        from app import app

        app.config["TESTING"] = True
        return app.test_client()

    def test_health_endpoint(self, client):
        """Test /health endpoint."""
        with patch("routes.ai_routes.chroma_client") as mock_chroma:
            with patch("routes.ai_routes.cache_manager") as mock_cache:
                mock_chroma.get_doc_count.return_value = 10
                mock_cache.get_stats.return_value = {"hits": 5}

                response = client.get("/api/ai/health")

                assert response.status_code == 200
                data = json.loads(response.data)
                assert data["status"] == "healthy"
                assert data["chroma_doc_count"] == 10

    def test_categorise_missing_content(self, client):
        """Test /categorise without content."""
        response = client.post("/api/ai/categorise", json={})

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Content is required" in data["error"]

    def test_query_missing_question(self, client):
        """Test /query without question."""
        response = client.post("/api/ai/query", json={})

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Question is required" in data["error"]

    def test_batch_process_exceeds_limit(self, client):
        """Test /batch-process with too many items."""
        items = [f"item_{i}" for i in range(21)]
        response = client.post("/api/ai/batch-process", json={"items": items})

        assert response.status_code == 400
