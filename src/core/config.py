from os.path import abspath
from os.path import dirname as up

from dotenv import load_dotenv
from pydantic import BaseSettings, Field

from src.logs.log_config import logger

load_dotenv('.env')


class Settings(BaseSettings):
    project_name: str = Field(..., env='PROJECT_NAME')
    db_host: str = Field(..., env='DB_HOST')
    db_port: int = Field(5432, env='DB_PORT')
    db_name: str = Field(..., env='DB_NAME')
    db_user: str = Field(..., env='DB_USER')
    db_password: str = Field(..., env='DB_PASSWORD')
    redis_host: str = Field(..., env='REDIS_HOST')
    redis_port: int = Field(6379, env='REDIS_PORT')
    base_dir: str = Field(up(up(up(abspath(__file__)))), env='BASE_DIR')
    cache_expire_in_seconds: int = Field(300000, env='CACHE_EXPIRE_IN_SECONDS')
    log_level: str = Field('INFO', env='LOG_LEVEL')

    class Config:
        env_file = '.env'


settings = Settings()
