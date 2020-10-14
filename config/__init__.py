# -*- coding: utf-8 -*-
# pylint: disable=C0103

"""
Configuration file for the whole project
"""
import os
import logging
from flask import Flask


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


def create_app(config, database):
    """
    Create app
    """

    # app initialization
    app = Flask(__name__)

    app.config.from_object(config)

    # db initialization
    database.init_app(app)

    # database.create_all(app=app) when use need to re-initialize db
    return app
