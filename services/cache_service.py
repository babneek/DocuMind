"""
Caching service for DocuMind - provides embedding and query response caching
"""

import json
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

class CacheManager:
    """Manages embedding and query response caching"""
    
    def __init__(self, max_memory_mb: int = 500):
        self.embedding_cache: Dict[str, List[float]] = {}  # text -> embedding vector
        self.response_cache: Dict[str, Dict[str, Any]] = {}  # query_hash -> response
        self.cache_times: Dict[str, datetime] = {}
        self.max_memory_mb = max_memory_mb
        self.current_memory_mb = 0
        
    def _hash_key(self, key: str) -> str:
        """Generate hash key for cache"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get cached embedding for text"""
        key = self._hash_key(text)
        if key in self.embedding_cache:
            self.cache_times[key] = datetime.now()  # Update access time
            return self.embedding_cache[key]
        return None
    
    def set_embedding(self, text: str, embedding: List[float]) -> None:
        """Cache embedding for text"""
        key = self._hash_key(text)
        
        # Estimate size (rough approximation)
        embedding_size_mb = len(embedding) * 4 / (1024 * 1024)  # 4 bytes per float32
        
        if self.current_memory_mb + embedding_size_mb > self.max_memory_mb:
            self._evict_oldest_embedding()
        
        self.embedding_cache[key] = embedding
        self.cache_times[key] = datetime.now()
        self.current_memory_mb += embedding_size_mb
    
    def get_response(self, query: str, doc_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get cached response for query"""
        cache_key = self._hash_key(f"{query}_{doc_id}")
        
        if cache_key in self.response_cache:
            cached = self.response_cache[cache_key]
            # Check if cache is still fresh (1 hour TTL)
            if (datetime.now() - cached['timestamp']).seconds < 3600:
                self.cache_times[cache_key] = datetime.now()
                return cached['response']
            else:
                del self.response_cache[cache_key]
        return None
    
    def set_response(self, query: str, response: Dict[str, Any], doc_id: Optional[int] = None) -> None:
        """Cache response for query"""
        cache_key = self._hash_key(f"{query}_{doc_id}")
        self.response_cache[cache_key] = {
            'timestamp': datetime.now(),
            'response': response
        }
        self.cache_times[cache_key] = datetime.now()
    
    def _evict_oldest_embedding(self) -> None:
        """Remove oldest embedding when cache is full"""
        if not self.cache_times:
            return
        
        # Find oldest cache entry
        oldest_key = min(self.cache_times, key=self.cache_times.get)
        
        if oldest_key in self.embedding_cache:
            embedding = self.embedding_cache.pop(oldest_key)
            embedding_size_mb = len(embedding) * 4 / (1024 * 1024)
            self.current_memory_mb -= embedding_size_mb
        
        if oldest_key in self.cache_times:
            del self.cache_times[oldest_key]
    
    def clear(self) -> None:
        """Clear all caches"""
        self.embedding_cache.clear()
        self.response_cache.clear()
        self.cache_times.clear()
        self.current_memory_mb = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "embedding_cache_size": len(self.embedding_cache),
            "response_cache_size": len(self.response_cache),
            "memory_used_mb": round(self.current_memory_mb, 2),
            "max_memory_mb": self.max_memory_mb
        }

# Global cache instance
_cache_instance = None

def get_cache_manager() -> CacheManager:
    """Get or create global cache manager instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheManager()
    return _cache_instance
