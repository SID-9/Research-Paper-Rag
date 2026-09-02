import redis
from app.core.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True,
    # remember these parameters will block ctrl+c from stopping task form terminal so activate later
    # socket_timeout=None,
    # socket_connect_timeout=None,
)