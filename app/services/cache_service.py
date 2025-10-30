"""
Caching service for performance optimization
"""
from typing import Optional, Any
import json
import hashlib
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# Simple in-memory cache (can be replaced with Redis)
_cache = {}
_cache_enabled = True


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments"""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(ttl: int = 300):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds (default: 5 minutes)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not _cache_enabled:
                return func(*args, **kwargs)
            
            key = f"{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Check cache
            if key in _cache:
                entry = _cache[key]
                import time
                if time.time() - entry["timestamp"] < ttl:
                    return entry["value"]
                else:
                    del _cache[key]
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            import time
            _cache[key] = {
                "value": result,
                "timestamp": time.time()
            }
            
            return result
        
        return wrapper
    return decorator


def clear_cache(pattern: Optional[str] = None):
    """
    Clear cache entries
    
    Args:
        pattern: Optional pattern to match keys (clears all if None)
    """
    if pattern:
        keys_to_delete = [k for k in _cache.keys() if pattern in k]
        for key in keys_to_delete:
            del _cache[key]
    else:
        _cache.clear()


def get_cache_stats():
    """Get cache statistics"""
    import time
    active_entries = sum(
        1 for entry in _cache.values()
        if time.time() - entry["timestamp"] < 300
    )
    return {
        "total_entries": len(_cache),
        "active_entries": active_entries,
        "enabled": _cache_enabled
    }

