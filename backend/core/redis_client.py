"""
Redis client for token blacklisting.
Gracefully degrades if Redis is unavailable (blacklist disabled).
"""

import redis
import os
from core.logger import logger

_redis_client = None


def get_redis():
    """Get or create Redis connection. Returns None if unavailable."""
    global _redis_client
    if _redis_client is None:
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            try:
                _redis_client = redis.from_url(redis_url, decode_responses=True)
                _redis_client.ping()
                logger.info("Redis connected for token blacklisting")
            except redis.ConnectionError:
                logger.warning("Redis unavailable. Token blacklist disabled.")
                _redis_client = None
        else:
            logger.warning("REDIS_URL not set. Token blacklist disabled.")
    return _redis_client


def blacklist_token(jti: str, expires_in_seconds: int):
    """Add a JWT ID to the blacklist with auto-expiry matching token TTL."""
    r = get_redis()
    if r:
        try:
            r.setex(f"blacklist:{jti}", expires_in_seconds, "1")
        except redis.RedisError as e:
            logger.error(f"Failed to blacklist token: {e}")


def is_token_blacklisted(jti: str) -> bool:
    """Check if a JWT ID has been revoked."""
    r = get_redis()
    if r:
        try:
            return r.exists(f"blacklist:{jti}") > 0
        except redis.RedisError:
            return False
    return False
