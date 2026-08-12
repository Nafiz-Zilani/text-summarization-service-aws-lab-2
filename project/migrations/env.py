from logging.config import fileConfig
import os
import sys

from sqlalchemy import create_engine, pool
from alembic import context

# -------------------------------------------------------------------
# Add project root to Python path
# -------------------------------------------------------------------

sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

# -------------------------------------------------------------------
# Import SQLAlchemy Base and models
# -------------------------------------------------------------------

from app.db import Base
from app.models.sqlalchemy import *  # noqa: F401,F403


# -------------------------------------------------------------------
# Alembic Config
# -------------------------------------------------------------------

config = context.config


# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# -------------------------------------------------------------------
# SQLAlchemy metadata
# -------------------------------------------------------------------

target_metadata = Base.metadata


# -------------------------------------------------------------------
# Database URL
# -------------------------------------------------------------------

def get_database_url() -> str:
    """
    Get database URL from the environment.

    Docker Compose provides:

    DATABASE_URL=postgresql+psycopg://postgres:postgres@web-db:5432/web_dev
    """

    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return database_url

    database_url = config.get_main_option("sqlalchemy.url")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable or "
            "sqlalchemy.url must be configured."
        )

    return database_url


# -------------------------------------------------------------------
# Offline migrations
# -------------------------------------------------------------------

def run_migrations_offline() -> None:
    """
    Run migrations in offline mode.
    """

    url = get_database_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# -------------------------------------------------------------------
# Online migrations
# -------------------------------------------------------------------

def run_migrations_online() -> None:
    """
    Run migrations in online mode.
    """

    database_url = get_database_url()

    connectable = create_engine(
        database_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# -------------------------------------------------------------------
# Run migration
# -------------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
