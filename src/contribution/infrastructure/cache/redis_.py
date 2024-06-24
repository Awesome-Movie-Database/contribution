from redis.asyncio import Redis

from contribution.infrastructure.cache import RedisConfig


def redis_factory(redis_config: RedisConfig) -> Redis:
    return Redis.from_url(
        url=redis_config.url,
        decode_responses=True,
    )