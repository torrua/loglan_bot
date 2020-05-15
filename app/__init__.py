# -*- coding: utf-8 -*-
# pylint: disable = C0103, C0413

"""
Initializing application module
Create an application object and database
"""

from os import environ

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


class Config:
    """
    Configuration object for remote database
    """
    SQLALCHEMY_DATABASE_URI = environ.get('LOD_DATABASE_URL')
    SQLALCHEMY_BINDS = {"user_database": environ.get('DATABASE_URL'), }
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
session = db.session(autoflush=True, autocommit=False)

EN = "en"
DEFAULT_LANGUAGE = environ.get('DEFAULT_LANGUAGE', EN)
SEPARATOR = "@"

from app import model_dictionary, model_user, routes
