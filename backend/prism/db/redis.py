"""
PRISM Redis Client — Connection management for caching and queues.
"""

import redis.asyncio as redis

from prism.config import settings

redis_client = redis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
)


async def check_redis_connection() -> None:
    """Verify Redis connectivity for health checks."""
    await redis_client.ping()
