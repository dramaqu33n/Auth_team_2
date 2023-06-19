from redis import Redis

from src.logs.log_config import logger
from src.core.config import settings
from utils.backoff import backoff


@backoff(exceptions=(ValueError,), start_sleep_time=0.1, factor=2, border_sleep_time=20)
def connect_to_redis(redis_host: str, redis_port: int) -> None:
    redis_client = Redis(host=redis_host, port=redis_port)
    if not redis_client.ping():
        raise ValueError('Redis not yet available. One more try.')
    logger.info('Successfully connected to Redis.')
    return None


if __name__ == '__main__':
    redis_host = settings.redis_host
    redis_port = settings.redis_port
    connect_to_redis(redis_host, redis_port)
