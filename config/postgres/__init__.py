# -*- coding: utf-8 -*-
# pylint: disable = C0103, C0413

"""
Initializing application module
Create an application object and database
"""
import os

from flask_sqlalchemy import SQLAlchemy

from config import log, create_app

db = SQLAlchemy()

from config.postgres import models


class CLIConfig:
    """
    Configuration object for remote database
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('LOD_DATABASE_URL', None)
    SQLALCHEMY_BINDS = {"user_database": os.environ.get('DATABASE_URL'), }
    SQLALCHEMY_TRACK_MODIFICATIONS = False


def app_lod(config_lod=CLIConfig, database=db):
    """
    Create LOD app with specified Config
    :param config_lod: Database Config
    :param database: SQLAlchemy() Database
    :return: flask.app.Flask
    """
    return create_app(config_lod, database=database)


def run_with_context(function):
    """Context Decorator"""
    def wrapper(*args, **kwargs):

        db_uri = os.environ.get('LOD_DATABASE_URL', None)
        db_users = os.environ.get('DATABASE_URL', None)

        if not db_uri:
            log.error("Please, specify 'LOD_DATABASE_URL' variable.")
            return

        if not db_users:
            log.error("Please, specify 'DATABASE_URL' variable.")
            return

        try:
            context = app_lod().app_context()
        except ValueError as err:
            log.error(err)
            return

        context.push()
        function(*args, **kwargs)
        context.pop()

    return wrapper


app = app_lod()


if __name__ == "__main__":

    with app_lod().app_context():
        pass
