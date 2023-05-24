from src.db.db_config import db_session
from src.db.model import Alembic
from alembic.config import Config
from alembic import command
from src.logs.log_config import logger
from sqlalchemy.exc import ProgrammingError


def do_init_migration() -> bool:
    try:
        query = db_session.query(Alembic).all()
        query = [el.version_num for el in query]
        if query:
            logger.info(f'Seems like initial migrations have been applied.')
            return False
    except ProgrammingError:
        logger.info('Migrations table does not exist')
    
    logger.info(f'Applying migrations')
    alembic_cfg = Config("alembic.ini")  # Path to your Alembic configuration file
    command.revision(alembic_cfg, autogenerate=True, message="Initial migration")
    command.upgrade(alembic_cfg, "head")

    return True

if __name__ == '__main__':
   do_init_migration()

