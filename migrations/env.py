"""Alembic migration environment - Standalone (no Flask dependency).

Uses SQLAlchemy 2.0 async models directly.
"""

import logging
from logging.config import fileConfig
from os import getenv

from sqlalchemy import create_engine, pool
from alembic import context

# Import all models so Alembic can detect them for autogenerate
from src.entities.base import Base
from src.entities.chat_session import ChatSession
from src.entities.chat_message import ChatMessage

config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

# Get database URL from environment (use sync driver for migrations)
def get_url():
    url = getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///db.sqlite")
    # Alembic uses sync drivers, so don't convert to async
    return url

# Set the URL in alembic config
config.set_main_option('sqlalchemy.url', get_url())

# Use our models' metadata for autogenerate
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
