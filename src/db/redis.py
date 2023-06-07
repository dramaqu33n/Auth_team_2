import hashlib
from enum import Enum
from redis import StrictRedis

from src.core.config import settings


class TokenType(Enum):
    ACCESS = 'access'
    REFRESH = 'refresh'


class TokenStorage:
    def __init__(self):
        self.redis = StrictRedis(
            host=settings.redis_host,
            port=settings.redis_port
        )

    def generate_key(self, token_type, user_id, user_agent):
        key = f"{token_type}:{user_id}:{user_agent}"
        return hashlib.sha256(key.encode()).hexdigest()

    def store_token(self, token_type, user_id, user_agent, token, ttl=None):
        key = self.generate_key(token_type, user_id, user_agent)
        if token_type == TokenType.ACCESS:
            if not ttl:
                ttl = settings.access_token_ttl
            self.redis.set(key, token, ttl)
        else:
            if not ttl:
                ttl = settings.refresh_token_ttl
            self.redis.set(key, token, ttl)

    def get_token(self, token_type, user_id, user_agent):
        key = self.generate_key(token_type, user_id, user_agent)
        return self.redis.get(key)

    def invalidate_token(self, token_type, user_id, user_agent):
        key = self.generate_key(token_type, user_id, user_agent)
        self.redis.delete(key)
