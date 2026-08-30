"""Database Engine and Async Session Factory"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.config import settings
from app.logger import log


def create_engine(database_url: str, echo: bool = False) -> AsyncEngine:
    """Creates an async SQLAlchemy engine with optimized connection pooling."""
    if not database_url:
        log.warning("Database URL is not configured. Falling back to in-memory SQLite.")
        database_url = "sqlite+aiosqlite:///:memory:"

    # If sqlite, use NullPool / basic settings
    if database_url.startswith("sqlite"):
        return create_async_engine(
            database_url,
            echo=echo,
            poolclass=NullPool,
        )

    # Postgres or other standard RDBMS
    return create_async_engine(
        database_url,
        echo=echo,
        pool_size=5,
        max_overflow=10,
        pool_recycle=300,
        pool_pre_ping=True,
    )


engine = create_engine(settings.database_url, echo=settings.sql_echo)

async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)
