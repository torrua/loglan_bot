from __future__ import annotations

import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


SQLALCHEMY_DATABASE_URL = os.getenv("LOD_DATABASE_URL_ASYNC")
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
async_session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)
