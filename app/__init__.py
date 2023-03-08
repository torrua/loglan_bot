import os

from flask import Flask
from app.routes import app_routes


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
