"""
In-memory cache manager (Redis-like)
LRU cache for hash lookups and performance optimization
"""
from collections import OrderedDict
import time
from backend.config import Config


class CacheManager:
    """In-memory LRU cache for performance optimization"""
    
    def __init__(self, max_size=None, ttl=None):
        """
        Initialize cache manager
        
        Args:
            max_size: Maximum number of cached items
            ttl: Time to live in seconds
        """
        self.max_size = max_size or Config.CACHE_MAX_SIZE
        self.ttl = ttl or Config.CACHE_TTL
        self.cache = OrderedDict()
        self.timestamps = {}
        self.hits = 0
        self.misses = 0
    
    def get(self, key):
        """
        Get value from cache
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None
        """
        if key not in self.cache:
            self.misses += 1
            return None
        
        # Check TTL
        if key in self.timestamps:
            age = time.time() - self.timestamps[key]
            if age > self.ttl:
                # Expired
                del self.cache[key]
                del self.timestamps[key]
                self.misses += 1
                return None
        
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        self.hits += 1
        return self.cache[key]
    
    def set(self, key, value):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
        """
        # Update existing key
        if key in self.cache:
            self.cache.move_to_end(key)
        
        self.cache[key] = value
        self.timestamps[key] = time.time()
        
        # Evict oldest if over max size
        if len(self.cache) > self.max_size:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            if oldest_key in self.timestamps:
                del self.timestamps[oldest_key]
    
    def delete(self, key):
        """
        Delete key from cache
        
        Args:
            key: Cache key
        """
        if key in self.cache:
            del self.cache[key]
        if key in self.timestamps:
            del self.timestamps[key]
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.timestamps.clear()
        self.hits = 0
        self.misses = 0
    
    def exists(self, key):
        """
        Check if key exists in cache
        
        Args:
            key: Cache key
        
        Returns:
            bool: True if exists and not expired
        """
        if key not in self.cache:
            return False
        
        # Check TTL
        if key in self.timestamps:
            age = time.time() - self.timestamps[key]
            if age > self.ttl:
                del self.cache[key]
                del self.timestamps[key]
                return False
        
        return True
    
    def cleanup_expired(self):
        """Remove all expired entries"""
        current_time = time.time()
        expired_keys = []
        
        for key, timestamp in self.timestamps.items():
            if current_time - timestamp > self.ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
            del self.timestamps[key]
        
        return len(expired_keys)
    
    def get_stats(self):
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': round(hit_rate, 2),
            'ttl_seconds': self.ttl
        }


# Global cache instance
_hash_cache = None


def get_hash_cache():
    """Get global hash cache instance"""
    global _hash_cache
    if _hash_cache is None:
        _hash_cache = CacheManager()
    return _hash_cache
