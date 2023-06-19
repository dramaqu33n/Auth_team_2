import psycopg2
from psycopg2 import OperationalError
from src.logs.log_config import logger
from src.core.config import settings
from utils.backoff import backoff

@backoff(exceptions = (OperationalError,ValueError), start_sleep_time=0.1, factor=2, border_sleep_time=20)
def connect_to_postgres(
    dbname: str,
    user: str,
    password: str,
    host: str,
    port: int
) -> None:
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.close()
    except OperationalError as e:
        logger.info(e)
        logger.info(dbname)
        logger.info(user)
        logger.info(password)
        logger.info(host)
        logger.info(port)
        raise ValueError('Postgres not yet available. One more try.')
    logger.info('Successfully connected to Postgres.')
    return None


if __name__ == '__main__':
    dbname = settings.db_name
    user = settings.db_user
    password = settings.db_password
    host = settings.db_host
    port = settings.db_port
    connect_to_postgres(dbname, user, password, host, port)
