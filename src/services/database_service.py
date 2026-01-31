"""Async database service using SQLAlchemy 2.0.

Provides async database session management.
- Local dev: SQLite with aiosqlite driver
- Production: PostgreSQL with asyncpg driver
"""

from os import getenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


def get_database_url() -> str:
    """Convert database URL to async driver format.
    
    Converts:
    - postgresql:// → postgresql+asyncpg://
    - sqlite:// → sqlite+aiosqlite://
    
    Note: For asyncpg, use 'ssl=require' instead of 'sslmode=require' in your URL.
    Example: postgresql://user:pass@host/db?ssl=require
    """
    url = getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///db.sqlite")
    
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("sqlite://"):
        url = url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    
    return url


engine = create_async_engine(get_database_url(), echo=False)

# Session factory - creates fresh sessions per request (essential for serverless)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """FastAPI dependency for database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()