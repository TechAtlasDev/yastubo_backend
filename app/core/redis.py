import redis.asyncio as redis
from app.core.config import settings

redis_client: redis.Redis = redis.from_url(
    settings.REDIS_URL, encoding="utf-8", decode_responses=True
)


async def get_redis():
    return redis_client


async def check_redis_connection() -> bool:
    try:
        await redis_client.ping()
        return True
    except Exception:
        return False
