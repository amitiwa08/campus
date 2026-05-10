"""
Redis caching layer for AI responses.
AI Developer 2 responsibility.
"""

import logging
import hashlib
import json
from typing import Optional, Dict, Any
import redis
import os

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Redis-based cache for AI responses.
    Features:
    - SHA256 cache keys
    - 15-minute TTL
    - Hit/miss tracking
    - Skip cache on fresh request flag
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        ttl_seconds: int = 900,  # 15 minutes
    ):
        self.ttl_seconds = ttl_seconds
        self.host = host
        self.port = port
        self.db = db
        self.hits = 0
        self.misses = 0

        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=True,
                socket_connect_timeout=5,
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {host}:{port}")
        except redis.ConnectionError as e:
            logger.warning(f"Redis connection failed: {e}. Cache disabled.")
            self.redis_client = None

    def _generate_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate SHA256 cache key from endpoint and parameters."""
        key_str = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
        return hashlib.sha256(key_str.encode()).hexdigest()

    def get(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get cached response if available.

        Args:
            endpoint: API endpoint name
            params: Request parameters

        Returns:
            Cached response dict or None
        """
        if not self.redis_client:
            self.misses += 1
            return None

        try:
            key = self._generate_key(endpoint, params)
            cached = self.redis_client.get(key)

            if cached:
                self.hits += 1
                logger.debug(f"Cache hit for {endpoint}")
                return json.loads(cached)
            else:
                self.misses += 1
                logger.debug(f"Cache miss for {endpoint}")
                return None

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self.misses += 1
            return None

    def set(
        self,
        endpoint: str,
        params: Dict[str, Any],
        value: Dict[str, Any],
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Cache a response.

        Args:
            endpoint: API endpoint name
            params: Request parameters
            value: Response to cache
            ttl: Custom TTL in seconds (default 900)

        Returns:
            True if successful
        """
        if not self.redis_client:
            return False

        try:
            key = self._generate_key(endpoint, params)
            ttl = ttl or self.ttl_seconds
            self.redis_client.setex(key, ttl, json.dumps(value))
            logger.debug(f"Cached response for {endpoint} with TTL {ttl}s")
            return True

        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False

    def clear_endpoint(self, endpoint: str) -> int:
        """Clear all cache entries for an endpoint."""
        if not self.redis_client:
            return 0

        try:
            pattern = f"*{endpoint}*"
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Cleared {deleted} cache entries for {endpoint}")
                return deleted
            return 0

        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0

        return {
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total,
            "hit_rate": f"{hit_rate:.1f}%",
            "redis_connected": self.redis_client is not None,
        }
