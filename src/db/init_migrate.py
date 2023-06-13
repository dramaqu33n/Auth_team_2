# from alembic import command
# from alembic.config import Config
# from sqlalchemy.exc import ProgrammingError

# from src.db.db_config import db_session
# from src.db.model import Alembic
# from src.logs.log_config import logger


# def do_init_migration() -> bool:
#     try:
#         query = db_session.query(Alembic).all()
#         query = [el.version_num for el in query]
#         if query:
#             logger.info('Seems like initial migrations have been applied.')
#             return False
#     except ProgrammingError:
#         logger.info('Migrations table does not exist')
#     logger.info('Applying migrations')
#     alembic_cfg = Config("alembic.ini")
#     command.revision(alembic_cfg, autogenerate=True, message="Initial migration")
#     command.upgrade(alembic_cfg, "head")
#     return True


# if __name__ == '__main__':
#     do_init_migration()

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.environment import EnvironmentContext
from sqlalchemy.exc import ProgrammingError

from src.db.db_config import db_session
from src.logs.log_config import logger


from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.environment import EnvironmentContext
from sqlalchemy.exc import ProgrammingError

from src.db.db_config import db_session
from src.logs.log_config import logger


def do_init_migration() -> bool:
    alembic_cfg = Config("alembic.ini")
    script = ScriptDirectory.from_config(alembic_cfg)

    connection = db_session.get_bind().connect()

    with EnvironmentContext(
        alembic_cfg,
        script,
        fn=lambda: script.get_current_head(),
    ) as env_context:
        env_context.configure(connection, script.as_revision_number)
        current_revision = env_context.get_head_revision()

    if current_revision is not None:
        logger.info('Seems like initial migrations have been applied.')
        return False

    logger.info('Applying migrations')
    command.revision(alembic_cfg, autogenerate=True, message="Initial migration")
    command.upgrade(alembic_cfg, "head")
    return True


if __name__ == '__main__':
    do_init_migration()