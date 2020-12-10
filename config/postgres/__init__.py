# -*- coding: utf-8 -*-
# pylint: disable = C0103, C0413

"""
Initializing application module
Create an application object and database
"""
import os
from loglan_db import app_lod


class CLIConfig:
    """
    Configuration object for remote database
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('LOD_DATABASE_URL', None)
    SQLALCHEMY_BINDS = {"user_database": os.environ.get('DATABASE_URL'), }
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app = app_lod(config_lod=CLIConfig)

from app import routes
