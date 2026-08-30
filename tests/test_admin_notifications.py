"""Tests for Admin Query Notifications and /spy command"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.bot.telegram.handlers.commands import bot_cmd_spy
from app.bot.telegram.notifications import (
    AdminNotificationManager,
    admin_notifications,
    notify_admin_query,
)


def test_notification_manager():
    mgr = AdminNotificationManager(initial_enabled=True)
    assert mgr.is_enabled is True

    mgr.toggle()
    assert mgr.is_enabled is False

    mgr.set_enabled(True)
    assert mgr.is_enabled is True


@pytest.mark.asyncio
async def test_notify_admin_query_for_other_user():
    other_user = SimpleNamespace(id=99999, username="john_doe", first_name="John", last_name="Doe")

    admin_notifications.set_enabled(True)
    with patch("app.bot.telegram.notifications.ADMIN", 12345):
        with patch("app.bot.telegram.notifications.bot.send_message", AsyncMock()) as mock_send:
            await notify_admin_query(other_user, "kliri", query_type="Search")
            mock_send.assert_called_once()
            args, kwargs = mock_send.call_args
            assert kwargs["chat_id"] == 12345
            assert "kliri" in kwargs["text"]
            assert "@john_doe" in kwargs["text"]


@pytest.mark.asyncio
async def test_notify_admin_query_ignored_for_admin_himself():
    admin_user = SimpleNamespace(id=12345, username="admin_user", first_name="Admin", last_name="")

    admin_notifications.set_enabled(True)
    with patch("app.bot.telegram.notifications.ADMIN", 12345):
        with patch("app.bot.telegram.notifications.bot.send_message", AsyncMock()) as mock_send:
            await notify_admin_query(admin_user, "kliri", query_type="Search")
            mock_send.assert_not_called()


@pytest.mark.asyncio
async def test_notify_admin_query_when_disabled():
    other_user = SimpleNamespace(id=99999, username="john_doe", first_name="John", last_name="Doe")

    admin_notifications.set_enabled(False)
    with patch("app.bot.telegram.notifications.ADMIN", 12345):
        with patch("app.bot.telegram.notifications.bot.send_message", AsyncMock()) as mock_send:
            await notify_admin_query(other_user, "kliri", query_type="Search")
            mock_send.assert_not_called()
    admin_notifications.set_enabled(True)


@pytest.mark.asyncio
async def test_bot_cmd_spy_toggle_by_admin():
    admin_msg = SimpleNamespace(
        chat=SimpleNamespace(id=12345),
        from_user=SimpleNamespace(id=12345),
        text="/spy",
    )

    with patch("app.bot.telegram.handlers.commands.ADMIN", 12345):
        with patch("app.bot.telegram.handlers.commands.bot.send_message", AsyncMock()) as mock_send:
            await bot_cmd_spy(admin_msg)  # type: ignore[arg-type]
            mock_send.assert_called_once()
            assert "Режим мониторинга запросов" in mock_send.call_args[1]["text"]


@pytest.mark.asyncio
async def test_bot_cmd_spy_on_and_off():
    admin_msg_off = SimpleNamespace(
        chat=SimpleNamespace(id=12345),
        from_user=SimpleNamespace(id=12345),
        text="/spy off",
    )
    admin_msg_on = SimpleNamespace(
        chat=SimpleNamespace(id=12345),
        from_user=SimpleNamespace(id=12345),
        text="/spy on",
    )

    with patch("app.bot.telegram.handlers.commands.ADMIN", 12345):
        with patch("app.bot.telegram.handlers.commands.bot.send_message", AsyncMock()) as mock_send:
            await bot_cmd_spy(admin_msg_off)  # type: ignore[arg-type]
            assert "выключен (OFF)" in mock_send.call_args[1]["text"]

            await bot_cmd_spy(admin_msg_on)  # type: ignore[arg-type]
            assert "включен (ON)" in mock_send.call_args[1]["text"]


@pytest.mark.asyncio
async def test_bot_cmd_spy_denied_for_regular_user():
    user_msg = SimpleNamespace(
        chat=SimpleNamespace(id=99999),
        from_user=SimpleNamespace(id=99999),
        text="/spy",
    )

    with patch("app.bot.telegram.handlers.commands.ADMIN", 12345):
        with patch("app.bot.telegram.handlers.commands.bot.send_message", AsyncMock()) as mock_send:
            await bot_cmd_spy(user_msg)  # type: ignore[arg-type]
            mock_send.assert_not_called()
