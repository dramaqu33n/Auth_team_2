from alembic import command
from alembic.config import Config
from sqlalchemy.exc import ProgrammingError

from src.db.db_config import db
from src.db.model import Alembic
from src.logs.log_config import logger


def do_init_migration() -> bool:
    try:
        query = db.session.query(Alembic).all()
        query = [el.version_num for el in query]
        if query:
            logger.info('Seems like initial migrations have been applied.')
            return False
    except ProgrammingError:
        logger.info('Migrations table does not exist')
    logger.info('Applying migrations')
    alembic_cfg = Config("alembic.ini")
    command.revision(alembic_cfg, autogenerate=True, message="Initial migration")
    command.upgrade(alembic_cfg, "head")
    return True


def do_second_migration() -> bool:
    alembic_cfg = Config("alembic.ini")
    command.revision(alembic_cfg, autogenerate=True, message="Adding user agent")
    command.upgrade(alembic_cfg, "head")
    return True


def do_partitioning() -> bool:
    alembic_cfg = Config("alembic.ini")
    command.revision(alembic_cfg, autogenerate=True, message="Access_history partioning")
    command.upgrade(alembic_cfg, "head")
    return True


if __name__ == '__main__':
    # do_init_migration()
    # do_second_migration()
    do_partitioning()
