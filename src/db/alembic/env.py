from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.orm import Session

from alembic import context

from src.core.config import settings
from src.db.db_config import Base
from src.db.model import User, Role

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata



def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    db_uri = f'postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}'
    context.configure(
        url=db_uri,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = context.config
    db_uri = f'postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}'
    configuration.set_main_option('sqlalchemy.url', db_uri)
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            session = Session(bind=connectable)

            # Look for a superuser
            superuser = session.query(User).filter(User.is_superuser).first()

            # If there's no superuser, create one
            if not superuser:
                superuser_role = session.query(Role).filter(Role.name == 'superuser').first()
                if not superuser_role:
                    superuser_role = Role(name='superuser')
                    session.add(superuser_role)
                    session.commit()

                # Assume you have a method to hash the password in User model
                superuser = User(username=settings.superuser_name, password=User.set_password(settings.superuser_pass), is_superuser=True, role=superuser_role)
                session.add(superuser)
                session.commit()
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
