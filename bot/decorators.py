"""
Decorators for Bot functions
"""

import time
from functools import wraps
from config import log


def logging_time(func):
    """
    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        def duration(start, end):
            return f'{end - start:.2f}'

        start_time = time.time()
        log.debug(
            "%s - Start time: %s", func.__name__,
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
        )
        result = func(*args, **kwargs)
        end_time = time.time()
        log.debug(
            "%s - End time: %s", func.__name__,
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
        )
        log.debug(
            "%s - Duration: %s seconds", func.__name__,
            duration(start_time, end_time)
        )
        return result
    return wrapper
