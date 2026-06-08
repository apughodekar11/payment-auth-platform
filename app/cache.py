import redis
from app.config import settings

_redis = redis.Redis.from_url(settings.redis_url, decode_responses=True)

def count_recent_transactions(card_token: str) -> int:
    key = f"velocity:{card_token}"
    count = _redis.incr(key) # create the key at 1 if it doesn't exist

    if count == 1:
        _redis.expire(key, settings.velocity_window_seconds) # set expiration only on first creation
    return count

# Used by the readiness probe to check if Redis is reachable
def is_reachable() -> bool:
    try:
        return _redis.ping()
    except redis.RedisError:
        return False