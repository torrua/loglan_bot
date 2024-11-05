import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

SQLALCHEMY_DATABASE_URI = os.environ.get("LOD_DATABASE_URL")
SQL_REQUESTS_ECHO = bool(int(os.environ.get("SQL_REQUESTS_ECHO", 0)))

if not SQLALCHEMY_DATABASE_URI:
    raise ValueError("LOD_DATABASE_URL is not set")

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URI,
    echo=SQL_REQUESTS_ECHO,
    pool_size=2,
    pool_recycle=5,
    max_overflow=0,
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    bind=engine,
    future=True,
    expire_on_commit=False,
)
