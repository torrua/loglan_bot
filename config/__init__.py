# -*- coding: utf-8 -*-
# pylint: disable=C0103

"""
Configuration file for the whole project
"""
import logging
import os

logging.basicConfig(
    # format='%(message)s',
    format="%(filename)s [LINE:%(lineno)d]"
    "\t[%(asctime)s] %(levelname)-s"
    "\t%(funcName)s() \t\t%(message)s",
    level=logging.DEBUG,
    datefmt="%y-%m-%d %H:%M:%S",
)

log = logging.getLogger(__name__)


EN, RU = "en", "ru"
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", EN)
DEFAULT_STYLE = os.getenv("DEFAULT_STYLE", "ultra")
SEPARATOR = "@"
