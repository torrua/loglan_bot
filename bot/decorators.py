import time
from functools import wraps
from config import log


def logging_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        log.debug(
            f"{func.__name__} - Start time:"
            f" {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
        result = func(*args, **kwargs)
        end_time = time.time()
        log.debug(
            f"{func.__name__} - End time:"
            f" {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
        log.debug(
            f"{func.__name__} - Duration:"
            f" {end_time - start_time:.2f} seconds")
        return result
    return wrapper
