# -*- coding: utf-8 -*-
"""The main module for launching web application"""

from app import create_app
from app.logger import log

app = create_app()
log.debug(app.name)
