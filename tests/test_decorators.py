"""Tests for function execution decorators"""

import asyncio

import pytest

from app.decorators import logging_time


def test_sync_logging_time():
    @logging_time
    def add(a: int, b: int) -> int:
        return a + b

    result = add(2, 3)
    assert result == 5


@pytest.mark.asyncio
async def test_async_logging_time():
    @logging_time
    async def async_add(a: int, b: int) -> int:
        await asyncio.sleep(0.01)
        return a + b

    result = await async_add(10, 20)
    assert result == 30


@pytest.mark.asyncio
async def test_async_logging_time_preserves_exceptions():
    @logging_time
    async def failing_task():
        await asyncio.sleep(0.01)
        raise ValueError("Task failed")

    with pytest.raises(ValueError, match="Task failed"):
        await failing_task()
