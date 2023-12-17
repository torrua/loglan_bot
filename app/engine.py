import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

SQLALCHEMY_DATABASE_URI = os.environ.get("LOD_DATABASE_URL")
SQL_REQUESTS_ECHO = bool(int(os.environ.get("SQL_REQUESTS_ECHO", 0)))
APP_NAME = os.environ.get("APP_NAME", "UNKNOWN")
engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
    pool_size=2,
    pool_recycle=5,
    max_overflow=0,
    pool_pre_ping=True,
    echo=SQL_REQUESTS_ECHO,
    connect_args={
        "application_name": APP_NAME,
    },
)
Session = scoped_session(sessionmaker(bind=engine, future=True))
