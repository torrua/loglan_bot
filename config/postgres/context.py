# -*- coding: utf-8 -*-

from config import log
from config.postgres import app


def run_with_context(function):
    log.info("run_into_context")

    def wrapper(*args, **kwargs):
        log.info("wrapper")

        try:
            context = app.app_context()
        except ValueError as err:
            log.error(err)
            return

        context.push()
        function(*args, **kwargs)
        context.pop()

    log.info("run_from_context")
    return wrapper
