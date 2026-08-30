"""Tests for Telegram Bot handlers and routes"""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.bot.telegram.handlers.commands import bot_cmd_gle, bot_cmd_log, bot_cmd_start
from app.bot.telegram.handlers.messages import bot_text_messages_handler
from app.bot.telegram.notifications import admin_notifications


@pytest.fixture(autouse=True)
def disable_admin_notifications_for_handler_tests():
    """Temporarily disables admin notifications during basic handler unit tests."""
    admin_notifications.set_enabled(False)
    yield
    admin_notifications.set_enabled(True)


@pytest.mark.asyncio
async def test_bot_cmd_start():
    msg = SimpleNamespace(
        chat=SimpleNamespace(id=12345),
        from_user=SimpleNamespace(id=12345, first_name="Test", username="testuser"),
    )

    with patch("app.bot.telegram.handlers.commands.bot.send_message", AsyncMock()) as mock_send:
        await bot_cmd_start(msg)  # type: ignore[arg-type]
        assert mock_send.call_count >= 1
        mock_send.assert_any_call(12345, "Loi!")


@pytest.mark.asyncio
async def test_bot_cmd_gle_empty():
    msg = SimpleNamespace(
        chat=SimpleNamespace(id=12345),
        from_user=SimpleNamespace(id=12345, first_name="Test", username="testuser"),
        text="/gle",
    )

    with patch("app.bot.telegram.handlers.commands.bot.send_message", AsyncMock()) as mock_send:
        await bot_cmd_gle(msg)  # type: ignore[arg-type]
        mock_send.assert_called_once()
        assert "specify the English word" in mock_send.call_args[1]["text"]


@pytest.mark.asyncio
async def test_bot_cmd_log_found(mock_word):
    msg = SimpleNamespace(
        chat=SimpleNamespace(id=12345),
        from_user=SimpleNamespace(id=12345, first_name="Test", username="testuser"),
        text="/log kliri",
    )

    with patch(
        "app.services.dictionary.DictionaryService.get_words_by_name",
        AsyncMock(return_value=[mock_word]),
    ):
        with patch("app.bot.telegram.handlers.commands.bot.send_message", AsyncMock()) as mock_send:
            await bot_cmd_log(msg)  # type: ignore[arg-type]
            mock_send.assert_called_once()
            assert "kliri" in mock_send.call_args[1]["text"]


@pytest.mark.asyncio
async def test_bot_text_message_handler(mock_word):
    msg = SimpleNamespace(
        chat=SimpleNamespace(id=12345),
        from_user=SimpleNamespace(id=12345, first_name="Test", username="testuser"),
        text="kliri",
    )

    with patch(
        "app.services.dictionary.DictionaryService.get_words_by_name",
        AsyncMock(return_value=[mock_word]),
    ):
        with patch("app.bot.telegram.handlers.commands.bot.send_message", AsyncMock()) as mock_send:
            await bot_text_messages_handler(msg)  # type: ignore[arg-type]
            mock_send.assert_called_once()
            assert "kliri" in mock_send.call_args[1]["text"]
