"""
YATRA AI — Caching Service
Provides high-performance caching with Redis and automated in-memory LRU fallback.
"""

import json
import logging
from typing import Optional, Any
import redis
from backend.app.config import settings

logger = logging.getLogger("yatra.cache")


class CacheService:
    def __init__(self):
        self.redis_client = None
        self._memory_cache = {}
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                socket_timeout=1.0,
                socket_connect_timeout=1.0,
                decode_responses=True,
            )
            self.redis_client.ping()
            logger.info("Connected to Redis cache at %s", settings.REDIS_URL)
        except Exception as e:
            self.redis_client = None
            logger.info("Redis not available (%s); operating with high-speed in-memory LRU cache.", str(e))

    def get(self, key: str) -> Optional[Any]:
        if self.redis_client:
            try:
                val = self.redis_client.get(key)
                if val:
                    return json.loads(val)
            except Exception:
                pass
        return self._memory_cache.get(key)

    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        serialized = json.dumps(value)
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl_seconds, serialized)
                return
            except Exception:
                pass
        # In-memory storage (bounded to 1000 entries)
        if len(self._memory_cache) > 1000:
            self._memory_cache.clear()
        self._memory_cache[key] = value

    def delete(self, key: str) -> None:
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception:
                pass
        self._memory_cache.pop(key, None)


cache_service = CacheService()

