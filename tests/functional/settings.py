from os.path import abspath
from os.path import dirname as up

from pydantic import BaseSettings


class Settings(BaseSettings):
    project_name: str
    db_host: str
    db_port: int = 5432
    db_name: str
    db_user: str
    db_password: str
    jaeger_host: str
    jaeger_port: int
    superuser_name: str
    superuser_pass: str
    secret_key: str
    redis_host: str
    redis_port: int = 6379
    access_token_ttl: int = 900  # 15 minutes
    refresh_token_ttl: int = 604800  # 1 week
    base_dir: str = up(up(up(abspath(__file__))))
    cache_expire_in_seconds: int = 300000
    log_level: str = 'INFO'
    vk_client_id: str
    vk_client_secret: str
    yandex_client_id: str
    yandex_client_secret: str

    class Config:
        env_file = '.env'


settings = Settings()
