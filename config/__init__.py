# -*- coding: utf-8 -*-
# pylint: disable=C0103

"""
Configuration file for the whole project
"""
import os
import logging
from loglan_db import app_lod

logging.basicConfig(
    # format='%(message)s',
    format='%(filename)s [LINE:%(lineno)d]\t[%(asctime)s] %(levelname)-s\t%(funcName)s() \t\t%(message)s',
    level=logging.DEBUG,
    datefmt="%y-%m-%d %H:%M:%S")

log = logging.getLogger(__name__)


EN, RU = "en", "ru"
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", EN)
DEFAULT_STYLE = os.getenv("DEFAULT_STYLE", "ultra")
SEPARATOR = "@"


class CLIConfig:
    """
    Configuration object for remote database
    """
    SQLALCHEMY_DATABASE_URI = os.environ.get('LOD_DATABASE_URL').replace("://", "ql://", 1)
    SQLALCHEMY_BINDS = {"user_database": os.environ.get('DATABASE_URL').replace("://", "ql://", 1), }
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app = app_lod(config_lod=CLIConfig)

from app import routes

