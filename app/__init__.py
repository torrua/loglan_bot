import os

from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.routes import app_routes

SQLALCHEMY_DATABASE_URI = os.environ.get('LOD_DATABASE_URL')
SQL_REQUESTS_ECHO = bool(int(os.environ.get('SQL_REQUESTS_ECHO', 0)))
APP_NAME = os.environ.get('APP_NAME', "UNKNOWN")

engine = create_engine(
    SQLALCHEMY_DATABASE_URI, pool_size=2,
    pool_recycle=5, max_overflow=0,
    pool_pre_ping=True, echo=SQL_REQUESTS_ECHO,
    connect_args={"application_name": APP_NAME, },
)
Session = scoped_session(sessionmaker(bind=engine, future=True))


def create_app(config):
    """
    Create app
    """

    new_app = Flask(__name__)

    new_app.config.from_object(config)
    new_app.register_blueprint(app_routes)
    return new_app


class CLIConfig:
    """
    Configuration object for remote database
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('LOD_DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

app = create_app(CLIConfig)

@app.teardown_appcontext
def cleanup(resp_or_exc):
    Session.remove()
