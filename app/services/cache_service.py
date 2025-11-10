"""
Redis Cache Service for Memory Optimization
Implements caching strategies for improved performance
"""
import redis
import json
import logging
from typing import Optional, Any, Dict
from app.core.config import settings
import hashlib

logger = logging.getLogger(__name__)


class CacheService:
    """Redis-based caching service for memory optimization"""
    
    def __init__(self):
        self.redis_client = None
        self._init_redis()
    
    def _init_redis(self):
        """Initialize Redis connection"""
        try:
            if settings.redis_url:
                self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
                # Test connection
                self.redis_client.ping()
                logger.info("Connected to Redis cache")
            else:
                logger.warning("Redis URL not configured. Caching disabled.")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    def _generate_key(self, prefix: str, *args) -> str:
        """Generate cache key from prefix and arguments"""
        key_parts = [prefix] + [str(arg) for arg in args]
        key_string = ":".join(key_parts)
        # Hash long keys
        if len(key_string) > 250:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"{prefix}:{key_hash}"
        return key_string
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL (default 1 hour)"""
        if not self.redis_client:
            return False
        
        try:
            serialized = json.dumps(value)
            return self.redis_client.setex(key, ttl, serialized)
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis_client:
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error deleting pattern from cache: {e}")
            return 0
    
    # Memory-specific caching methods
    
    def cache_memory(self, memory_id: str, memory_data: Dict[str, Any], ttl: int = 3600):
        """Cache memory data"""
        key = self._generate_key("memory", memory_id)
        return self.set(key, memory_data, ttl)
    
    def get_cached_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get cached memory"""
        key = self._generate_key("memory", memory_id)
        return self.get(key)
    
    def cache_search_results(self, query: str, results: list, ttl: int = 300):
        """Cache search results (5 min TTL)"""
        key = self._generate_key("search", query)
        return self.set(key, results, ttl)
    
    def get_cached_search(self, query: str) -> Optional[list]:
        """Get cached search results"""
        key = self._generate_key("search", query)
        return self.get(key)
    
    def cache_embedding(self, content: str, embedding: list, ttl: int = 86400):
        """Cache embeddings (24 hour TTL)"""
        key = self._generate_key("embedding", content)
        return self.set(key, embedding, ttl)
    
    def get_cached_embedding(self, content: str) -> Optional[list]:
        """Get cached embedding"""
        key = self._generate_key("embedding", content)
        return self.get(key)
    
    def invalidate_memory(self, memory_id: str):
        """Invalidate memory cache"""
        key = self._generate_key("memory", memory_id)
        self.delete(key)
        # Also invalidate related searches
        self.delete_pattern("search:*")
    
    def invalidate_all_memories(self):
        """Invalidate all memory caches"""
        self.delete_pattern("memory:*")
        self.delete_pattern("search:*")


# Global cache service instance
cache_service = CacheService()
