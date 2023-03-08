# -*- coding: utf-8 -*-
"""The main module for launching web application"""

from app import create_app, CLIConfig
app = create_app(CLIConfig)
