import os

from flask import Flask
from loglan_core.setup import engine
from sqlalchemy.orm import scoped_session, sessionmaker

Session = scoped_session(sessionmaker(bind=engine))


def create_app(config):
    """
    Create app
    """

    app = Flask(__name__)

    app.config.from_object(config)

    return app


class CLIConfig:
    """
    Configuration object for remote database
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('LOD_DATABASE_URL').replace("://", "ql://", 1)
    SQLALCHEMY_BINDS = {"user_database": os.environ.get('DATABASE_URL').replace("://", "ql://", 1), }
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app = create_app(CLIConfig)


@app.teardown_appcontext
def cleanup(resp_or_exc):
    Session.remove()
