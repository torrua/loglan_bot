import os

from flask import Flask
from loglan_core.setup import Session


def create_app(config):
    """
    Create app
    """

    new_app = Flask(__name__)

    new_app.config.from_object(config)

    return new_app


class CLIConfig:
    """
    Configuration object for remote database
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app = create_app(CLIConfig)


@app.teardown_appcontext
def cleanup(resp_or_exc):
    Session.remove()


from app import routes
