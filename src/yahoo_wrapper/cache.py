"""
Yahoo Fantasy Sports API Response Cache
Implements caching for API responses to reduce API calls and improve performance
"""

import json
import hashlib
import asyncio
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path
import aiofiles
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class CacheBackend:
    """Base cache backend interface"""
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get value from cache"""
        raise NotImplementedError
        
    async def set(self, key: str, value: Dict[str, Any], ttl: int = None):
        """Set value in cache with optional TTL in seconds"""
        raise NotImplementedError
        
    async def delete(self, key: str):
        """Delete value from cache"""
        raise NotImplementedError
        
    async def clear(self):
        """Clear all cache entries"""
        raise NotImplementedError
        
    async def close(self):
        """Close cache connections"""
        pass


class MemoryCache(CacheBackend):
    """In-memory cache backend"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._expiry: Dict[str, datetime] = {}
        
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get value from memory cache"""
        if key in self._cache:
            # Check if expired
            if key in self._expiry and datetime.now() > self._expiry[key]:
                await self.delete(key)
                return None
            return self._cache[key]
        return None
        
    async def set(self, key: str, value: Dict[str, Any], ttl: int = None):
        """Set value in memory cache"""
        self._cache[key] = value
        if ttl is not None:
            self._expiry[key] = datetime.now() + timedelta(seconds=ttl)
            
    async def delete(self, key: str):
        """Delete value from memory cache"""
        self._cache.pop(key, None)
        self._expiry.pop(key, None)
        
    async def clear(self):
        """Clear memory cache"""
        self._cache.clear()
        self._expiry.clear()


class FileCache(CacheBackend):
    """File-based cache backend"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
    def _get_cache_path(self, key: str) -> Path:
        """Get file path for cache key"""
        return self.cache_dir / f"{key}.json"
        
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get value from file cache"""
        cache_path = self._get_cache_path(key)
        
        if cache_path.exists():
            try:
                async with aiofiles.open(cache_path, 'r') as f:
                    data = json.loads(await f.read())
                    
                # Check expiry
                if 'expiry' in data and datetime.fromisoformat(data['expiry']) < datetime.now():
                    await self.delete(key)
                    return None
                    
                return data.get('value')
            except Exception as e:
                logger.error(f"Error reading cache file {cache_path}: {e}")
                return None
        return None
        
    async def set(self, key: str, value: Dict[str, Any], ttl: int = None):
        """Set value in file cache"""
        cache_path = self._get_cache_path(key)
        
        data = {'value': value}
        if ttl:
            data['expiry'] = (datetime.now() + timedelta(seconds=ttl)).isoformat()
            
        try:
            async with aiofiles.open(cache_path, 'w') as f:
                await f.write(json.dumps(data))
        except Exception as e:
            logger.error(f"Error writing cache file {cache_path}: {e}")
            
    async def delete(self, key: str):
        """Delete value from file cache"""
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()
            
    async def clear(self):
        """Clear file cache"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()


class RedisCache(CacheBackend):
    """Redis cache backend"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        
    async def _get_client(self) -> redis.Redis:
        """Get or create Redis client"""
        if not self.redis_client:
            self.redis_client = await redis.from_url(self.redis_url)
        return self.redis_client
        
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get value from Redis cache"""
        try:
            client = await self._get_client()
            value = await client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
        return None
        
    async def set(self, key: str, value: Dict[str, Any], ttl: int = None):
        """Set value in Redis cache"""
        try:
            client = await self._get_client()
            serialized = json.dumps(value)
            if ttl:
                await client.setex(key, ttl, serialized)
            else:
                await client.set(key, serialized)
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            
    async def delete(self, key: str):
        """Delete value from Redis cache"""
        try:
            client = await self._get_client()
            await client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            
    async def clear(self):
        """Clear Redis cache (use with caution)"""
        try:
            client = await self._get_client()
            await client.flushdb()
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()


class YahooAPICache:
    """Yahoo Fantasy Sports API cache manager"""
    
    # Default TTL values for different resource types (in seconds)
    DEFAULT_TTL = {
        'game': 86400,        # 24 hours
        'league': 3600,       # 1 hour
        'team': 1800,         # 30 minutes
        'player': 3600,       # 1 hour
        'roster': 300,        # 5 minutes
        'transaction': 300,   # 5 minutes
        'standings': 1800,    # 30 minutes
        'scoreboard': 300,    # 5 minutes
        'stats': 1800,        # 30 minutes
        'user': 3600,         # 1 hour
    }
    
    def __init__(self, backend: CacheBackend = None):
        self.backend = backend or MemoryCache()
        
    def _generate_cache_key(
        self, 
        resource_type: str, 
        resource_id: str, 
        params: Dict[str, Any] = None
    ) -> str:
        """Generate cache key from resource type, ID, and parameters"""
        key_parts = [resource_type, resource_id]
        
        if params:
            # Sort params for consistent key generation
            sorted_params = sorted(params.items())
            param_str = "&".join([f"{k}={v}" for k, v in sorted_params])
            key_parts.append(param_str)
            
        key_string = ":".join(key_parts)
        
        # Hash long keys
        if len(key_string) > 200:
            return hashlib.md5(key_string.encode()).hexdigest()
        
        return key_string.replace("/", "_").replace(" ", "_")
        
    def _get_ttl_for_resource(self, resource_type: str, custom_ttl: int = None) -> int:
        """Get TTL for resource type"""
        if custom_ttl:
            return custom_ttl
            
        # Extract base resource type from full type
        base_type = resource_type.split('_')[0]
        return self.DEFAULT_TTL.get(base_type, self.DEFAULT_TTL['league'])
        
    async def get(
        self, 
        resource_type: str, 
        resource_id: str, 
        params: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Get cached response"""
        key = self._generate_cache_key(resource_type, resource_id, params)
        
        try:
            cached = await self.backend.get(key)
            if cached:
                logger.debug(f"Cache hit for {key}")
                return cached
            logger.debug(f"Cache miss for {key}")
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            
        return None
        
    async def set(
        self, 
        resource_type: str, 
        resource_id: str, 
        value: Dict[str, Any],
        params: Dict[str, Any] = None,
        ttl: int = None
    ):
        """Set cached response"""
        key = self._generate_cache_key(resource_type, resource_id, params)
        ttl = self._get_ttl_for_resource(resource_type, ttl)
        
        try:
            await self.backend.set(key, value, ttl)
            logger.debug(f"Cached {key} with TTL {ttl}s")
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            
    async def invalidate(
        self, 
        resource_type: str, 
        resource_id: str, 
        params: Dict[str, Any] = None
    ):
        """Invalidate cached response"""
        key = self._generate_cache_key(resource_type, resource_id, params)
        
        try:
            await self.backend.delete(key)
            logger.debug(f"Invalidated cache for {key}")
        except Exception as e:
            logger.error(f"Cache invalidate error: {e}")
            
    async def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern (if backend supports it)"""
        # This would need to be implemented differently for each backend
        # For now, only Redis supports pattern matching
        if isinstance(self.backend, RedisCache):
            try:
                client = await self.backend._get_client()
                keys = await client.keys(pattern)
                if keys:
                    await client.delete(*keys)
                    logger.debug(f"Invalidated {len(keys)} keys matching {pattern}")
            except Exception as e:
                logger.error(f"Pattern invalidation error: {e}")
                
    async def clear_all(self):
        """Clear all cache entries"""
        try:
            await self.backend.clear()
            logger.info("Cleared all cache entries")
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            
    async def close(self):
        """Close cache backend connections"""
        await self.backend.close()


def create_cache(cache_type: str = "memory", **kwargs) -> YahooAPICache:
    """Factory function to create cache instance"""
    if cache_type == "memory":
        backend = MemoryCache()
    elif cache_type == "file":
        cache_dir = kwargs.get("cache_dir", "cache")
        backend = FileCache(cache_dir)
    elif cache_type == "redis":
        redis_url = kwargs.get("redis_url", "redis://localhost:6379")
        backend = RedisCache(redis_url)
    else:
        raise ValueError(f"Unknown cache type: {cache_type}")
        
    return YahooAPICache(backend)