"""Execution Timing and Performance Decorators"""

from __future__ import annotations

import asyncio
import functools
import time
from collections.abc import Callable
from typing import Any

from app.logger import log


def logging_time(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to measure and log execution time of both sync and async functions."""

    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            log.debug("%s - Started execution", func.__name__)
            try:
                return await func(*args, **kwargs)
            finally:
                duration = time.perf_counter() - start_time
                log.debug("%s - Completed in %.3f seconds", func.__name__, duration)

        return async_wrapper

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        log.debug("%s - Started execution", func.__name__)
        try:
            return func(*args, **kwargs)
        finally:
            duration = time.perf_counter() - start_time
            log.debug("%s - Completed in %.3f seconds", func.__name__, duration)

    return sync_wrapper
