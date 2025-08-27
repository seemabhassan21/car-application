import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

# --- Alembic Config ---
config = context.config

# Interpret config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def get_url() -> str:
    load_dotenv()
    url = os.getenv("ASYNC_DATABASE_URL")
    if not url:
        raise ValueError("ASYNC_DATABASE_URL is not set in .env file")
    return url


def get_target_metadata():
    """Dynamically import Base and models and return metadata.

    Doing this inside a function avoids module-level imports after executable
    statements (fixes flake8 E402) and ensures models are imported before
    Alembic autogenerate runs so all tables are registered.
    """
    # Ensure Alembic can find the "app" package
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

    # Import Base and models
    from app.core.database import Base  # noqa: WPS433
    import app.models.user  # noqa: F401, WPS433
    import app.models.cars  # noqa: F401, WPS433

    return Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=get_target_metadata(),
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Configure Alembic to use connection in online mode."""
    context.configure(
        connection=connection,
        target_metadata=get_target_metadata(),
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode with async engine."""
    connectable = create_async_engine(get_url(), poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
