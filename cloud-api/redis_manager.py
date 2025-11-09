"""
Redis connection manager for QuoTrading Cloud API
Handles rate limiting, caching, and session management
Falls back to in-memory if Redis unavailable
"""

import redis
from typing import Optional, Dict, Any
import os
import json
from collections import deque
import time as time_module

class RedisManager:
    """Manages Redis connections with fallback to in-memory storage"""
    
    def __init__(self, redis_url: Optional[str] = None, fallback_to_memory: bool = True):
        """
        Initialize Redis connection
        
        Args:
            redis_url: Redis connection URL (redis://host:port/db)
            fallback_to_memory: Use in-memory storage if Redis unavailable
        """
        self.redis_url = redis_url or os.getenv('REDIS_URL')
        self.fallback_to_memory = fallback_to_memory
        self.redis_client: Optional[redis.Redis] = None
        self.using_memory_fallback = False
        
        # In-memory fallback storage
        self.memory_store: Dict[str, Any] = {}
        self.rate_limit_storage: Dict[str, deque] = {}
        
        # Try to connect to Redis
        if self.redis_url:
            try:
                self.redis_client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                # Test connection
                self.redis_client.ping()
                print(f"✅ Connected to Redis: {self.redis_url}")
            except Exception as e:
                print(f"⚠️  Redis connection failed: {e}")
                if fallback_to_memory:
                    print("📦 Using in-memory fallback storage")
                    self.using_memory_fallback = True
                    self.redis_client = None
                else:
                    raise
        else:
            print("📦 No REDIS_URL provided - using in-memory storage")
            self.using_memory_fallback = True
    
    def _is_connected(self) -> bool:
        """Check if Redis is connected and available"""
        if self.redis_client is None:
            return False
        try:
            self.redis_client.ping()
            return True
        except:
            return False
    
    # === BASIC KEY-VALUE OPERATIONS ===
    
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """
        Set a key-value pair
        
        Args:
            key: Key name
            value: Value (will be JSON serialized if not string)
            ex: Expiration time in seconds
        
        Returns:
            True if successful
        """
        if self._is_connected():
            try:
                if not isinstance(value, str):
                    value = json.dumps(value)
                self.redis_client.set(key, value, ex=ex)
                return True
            except Exception as e:
                print(f"Redis SET error: {e}")
                if not self.fallback_to_memory:
                    raise
        
        # Fallback to memory
        self.memory_store[key] = {
            'value': value,
            'expires_at': time_module.time() + ex if ex else None
        }
        return True
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value by key
        
        Args:
            key: Key name
        
        Returns:
            Value or None if not found
        """
        if self._is_connected():
            try:
                value = self.redis_client.get(key)
                if value:
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        return value
                return None
            except Exception as e:
                print(f"Redis GET error: {e}")
                if not self.fallback_to_memory:
                    raise
        
        # Fallback to memory
        if key in self.memory_store:
            item = self.memory_store[key]
            # Check expiration
            if item['expires_at'] and time_module.time() > item['expires_at']:
                del self.memory_store[key]
                return None
            return item['value']
        return None
    
    def delete(self, key: str) -> bool:
        """Delete a key"""
        if self._is_connected():
            try:
                self.redis_client.delete(key)
                return True
            except Exception as e:
                print(f"Redis DELETE error: {e}")
                if not self.fallback_to_memory:
                    raise
        
        # Fallback to memory
        if key in self.memory_store:
            del self.memory_store[key]
        return True
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        if self._is_connected():
            try:
                return bool(self.redis_client.exists(key))
            except Exception as e:
                print(f"Redis EXISTS error: {e}")
                if not self.fallback_to_memory:
                    raise
        
        # Fallback to memory
        if key in self.memory_store:
            item = self.memory_store[key]
            if item['expires_at'] and time_module.time() > item['expires_at']:
                del self.memory_store[key]
                return False
            return True
        return False
    
    # === RATE LIMITING ===
    
    def check_rate_limit(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int,
        block_duration: int = 300
    ) -> dict:
        """
        Check if identifier is within rate limits (sliding window)
        
        Args:
            identifier: IP address or user ID
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            block_duration: How long to block if exceeded (seconds)
        
        Returns:
            {
                'allowed': bool,
                'requests_made': int,
                'requests_remaining': int,
                'retry_after': int (seconds until unblocked, if blocked)
            }
        """
        current_time = time_module.time()
        block_key = f"rate_limit:block:{identifier}"
        requests_key = f"rate_limit:requests:{identifier}"
        
        # Check if blocked
        if self._is_connected():
            try:
                blocked_until = self.redis_client.get(block_key)
                if blocked_until and float(blocked_until) > current_time:
                    return {
                        'allowed': False,
                        'requests_made': max_requests,
                        'requests_remaining': 0,
                        'retry_after': int(float(blocked_until) - current_time)
                    }
                
                # Add current request timestamp
                pipe = self.redis_client.pipeline()
                pipe.zadd(requests_key, {str(current_time): current_time})
                pipe.zremrangebyscore(requests_key, 0, current_time - window_seconds)
                pipe.zcard(requests_key)
                pipe.expire(requests_key, window_seconds)
                results = pipe.execute()
                
                requests_made = results[2]
                
                if requests_made > max_requests:
                    # Block the identifier
                    self.redis_client.setex(
                        block_key,
                        block_duration,
                        str(current_time + block_duration)
                    )
                    return {
                        'allowed': False,
                        'requests_made': requests_made,
                        'requests_remaining': 0,
                        'retry_after': block_duration
                    }
                
                return {
                    'allowed': True,
                    'requests_made': requests_made,
                    'requests_remaining': max_requests - requests_made,
                    'retry_after': 0
                }
                
            except Exception as e:
                print(f"Redis rate limit error: {e}")
                if not self.fallback_to_memory:
                    raise
        
        # Fallback to in-memory rate limiting (from original implementation)
        if identifier not in self.rate_limit_storage:
            self.rate_limit_storage[identifier] = {
                'requests': deque(),
                'blocked_until': None
            }
        
        storage = self.rate_limit_storage[identifier]
        
        # Check if blocked
        if storage['blocked_until'] and storage['blocked_until'] > current_time:
            return {
                'allowed': False,
                'requests_made': max_requests,
                'requests_remaining': 0,
                'retry_after': int(storage['blocked_until'] - current_time)
            }
        
        # Remove old timestamps
        while storage['requests'] and storage['requests'][0] < current_time - window_seconds:
            storage['requests'].popleft()
        
        # Add current request
        storage['requests'].append(current_time)
        requests_made = len(storage['requests'])
        
        if requests_made > max_requests:
            # Block the identifier
            storage['blocked_until'] = current_time + block_duration
            return {
                'allowed': False,
                'requests_made': requests_made,
                'requests_remaining': 0,
                'retry_after': block_duration
            }
        
        return {
            'allowed': True,
            'requests_made': requests_made,
            'requests_remaining': max_requests - requests_made,
            'retry_after': 0
        }
    
    def get_rate_limit_status(
        self,
        identifier: str,
        max_requests: int,
        window_seconds: int
    ) -> dict:
        """
        Get current rate limit status without incrementing counter
        
        Args:
            identifier: IP address or user ID
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
        
        Returns:
            Status dict with requests_made, requests_remaining, blocked info
        """
        current_time = time_module.time()
        block_key = f"rate_limit:block:{identifier}"
        requests_key = f"rate_limit:requests:{identifier}"
        
        if self._is_connected():
            try:
                # Check if blocked
                blocked_until = self.redis_client.get(block_key)
                if blocked_until and float(blocked_until) > current_time:
                    return {
                        'identifier': identifier,
                        'requests_made': max_requests,
                        'requests_remaining': 0,
                        'max_requests': max_requests,
                        'window_seconds': window_seconds,
                        'blocked': True,
                        'retry_after': int(float(blocked_until) - current_time)
                    }
                
                # Count requests in window
                self.redis_client.zremrangebyscore(requests_key, 0, current_time - window_seconds)
                requests_made = self.redis_client.zcard(requests_key)
                
                return {
                    'identifier': identifier,
                    'requests_made': requests_made,
                    'requests_remaining': max(0, max_requests - requests_made),
                    'max_requests': max_requests,
                    'window_seconds': window_seconds,
                    'blocked': False,
                    'retry_after': 0
                }
                
            except Exception as e:
                print(f"Redis rate limit status error: {e}")
                if not self.fallback_to_memory:
                    raise
        
        # Fallback to in-memory
        if identifier not in self.rate_limit_storage:
            return {
                'identifier': identifier,
                'requests_made': 0,
                'requests_remaining': max_requests,
                'max_requests': max_requests,
                'window_seconds': window_seconds,
                'blocked': False,
                'retry_after': 0
            }
        
        storage = self.rate_limit_storage[identifier]
        
        # Check if blocked
        if storage['blocked_until'] and storage['blocked_until'] > current_time:
            return {
                'identifier': identifier,
                'requests_made': max_requests,
                'requests_remaining': 0,
                'max_requests': max_requests,
                'window_seconds': window_seconds,
                'blocked': True,
                'retry_after': int(storage['blocked_until'] - current_time)
            }
        
        # Count valid requests
        while storage['requests'] and storage['requests'][0] < current_time - window_seconds:
            storage['requests'].popleft()
        
        requests_made = len(storage['requests'])
        
        return {
            'identifier': identifier,
            'requests_made': requests_made,
            'requests_remaining': max(0, max_requests - requests_made),
            'max_requests': max_requests,
            'window_seconds': window_seconds,
            'blocked': False,
            'retry_after': 0
        }
    
    def close(self):
        """Close Redis connection"""
        if self.redis_client:
            self.redis_client.close()
            print("✅ Redis connection closed")


# Global Redis manager instance
redis_manager: Optional[RedisManager] = None


def get_redis() -> RedisManager:
    """Get global Redis manager instance"""
    global redis_manager
    if redis_manager is None:
        redis_manager = RedisManager()
    return redis_manager
