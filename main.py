# -*- coding: utf-8 -*-
"""The main module for launching web application"""

from app import app
from app.logger import log

log.debug(app.name)
