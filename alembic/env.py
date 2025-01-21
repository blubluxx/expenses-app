import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/")))


from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool

from alembic import context

from app.core.config import get_settings
from app.sql_app.database import Base


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
settings = get_settings()


DATABASE_URL = settings.DATABASE_URL
DATABASE_URL_ALEMBIC = DATABASE_URL.replace("%", "%%")

config.set_main_option("sqlalchemy.url", DATABASE_URL_ALEMBIC)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
connectable = create_async_engine(
    DATABASE_URL,
    poolclass=pool.NullPool,  # Optional: Configure pool settings as needed
)

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


async def run_migrations():
    """Run migrations in 'online' mode."""
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


def do_run_migrations(connection):
    """Run migrations with the provided connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    import asyncio

    asyncio.run(run_migrations())


if context.is_offline_mode():
    context.configure(url=DATABASE_URL_ALEMBIC)
    with context.begin_transaction():
        context.run_migrations()
else:
    run_migrations_online()
