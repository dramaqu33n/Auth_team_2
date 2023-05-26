import hashlib
import secrets
from datetime import timedelta

from redis import StrictRedis

from core.config import settings


class TokenStorage:
    def __init__(self):
        self.redis = StrictRedis(
            host=settings.redis_host,
            port=settings.redis_port
        )

    def generate_key(self, token_type, user_id, user_agent):
        key = f"{token_type}:{user_id}:{user_agent}"
        return hashlib.sha256(key.encode()).hexdigest()

    def store_token(self, token_type, user_id, user_agent, token):
        key = self.generate_key(token_type, user_id, user_agent)
        if token_type == 'access':
            self.redis.set(key, token, settings.access_token_ttl)
        else:
            self.redis.set(key, token, settings.refresh_token_ttl)

    # def get_token(self, token_type, user_id, user_agent):
    #     key = self.generate_key(token_type, user_id, user_agent)
    #     return self.redis.get(key)

    # def invalidate_token(self, token_type, user_id, user_agent):
    #     key = self.generate_key(token_type, user_id, user_agent)
    #     self.redis.delete(key)
