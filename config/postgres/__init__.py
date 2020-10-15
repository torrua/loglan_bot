# -*- coding: utf-8 -*-
# pylint: disable = C0103, C0413

"""
Initializing application module
Create an application object and database
"""
import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from config.postgres import models


class CLIConfig:
    """
    Configuration object for remote database
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('LOD_DATABASE_URL', None)
    SQLALCHEMY_BINDS = {"user_database": os.environ.get('DATABASE_URL'), }
    SQLALCHEMY_TRACK_MODIFICATIONS = False


from config import create_app

app = create_app(config=CLIConfig, database=db)
from app import routes
