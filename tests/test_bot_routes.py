"""Tests for Telegram Bot webhook management routes and URL normalization"""

from unittest.mock import AsyncMock, patch

import pytest
from telebot.asyncio_helper import ApiTelegramException

from app.bot import _normalize_webhook_url


@pytest.mark.parametrize(
    "raw_input, expected_output",
    [
        ("example.com", "https://example.com/bot/webhook"),
        ("example.com/", "https://example.com/bot/webhook"),
        ("https://example.com", "https://example.com/bot/webhook"),
        ("https://example.com/", "https://example.com/bot/webhook"),
        ("http://example.com", "https://example.com/bot/webhook"),
        ("example.com/bot/webhook", "https://example.com/bot/webhook"),
        ("https://example.com/bot/webhook", "https://example.com/bot/webhook"),
        ("https://example.com:8443", "https://example.com:8443/bot/webhook"),
        ("example.com:8443/bot/webhook", "https://example.com:8443/bot/webhook"),
        ("", ""),
    ],
)
def test_normalize_webhook_url(raw_input: str, expected_output: str):
    assert _normalize_webhook_url(raw_input) == expected_output


@pytest.mark.asyncio
async def test_set_webhook_success(test_client):
    with patch("app.bot.bot.remove_webhook", AsyncMock()):
        with patch("app.bot.bot.set_webhook", AsyncMock()) as mock_set:
            response = await test_client.get("/bot/set?host=my-new-domain.com")
            assert response.status_code == 200
            data = await response.get_data(as_text=True)
            assert "⚓ Webhook set to: https://my-new-domain.com/bot/webhook" in data
            mock_set.assert_awaited_once_with(url="https://my-new-domain.com/bot/webhook")


@pytest.mark.asyncio
async def test_set_webhook_with_protocol_in_query(test_client):
    with patch("app.bot.bot.remove_webhook", AsyncMock()):
        with patch("app.bot.bot.set_webhook", AsyncMock()) as mock_set:
            response = await test_client.get("/bot/set?host=https://my-new-domain.com/")
            assert response.status_code == 200
            mock_set.assert_awaited_once_with(url="https://my-new-domain.com/bot/webhook")


@pytest.mark.asyncio
async def test_set_webhook_telegram_api_error(test_client):
    result_json = {"error_code": 400, "description": "Bad Request: invalid webhook URL specified"}
    api_error = ApiTelegramException("setWebhook", None, result_json)

    with patch("app.bot.bot.remove_webhook", AsyncMock()):
        with patch("app.bot.bot.set_webhook", AsyncMock(side_effect=api_error)):
            response = await test_client.get("/bot/set?host=invalid-host")
            assert response.status_code == 400
            json_data = await response.get_json()
            assert json_data["status"] == "error"
            assert "invalid webhook URL specified" in json_data["telegram_error"]
            assert json_data["attempted_url"] == "https://invalid-host/bot/webhook"


@pytest.mark.asyncio
async def test_delete_webhook(test_client):
    with patch("app.bot.bot.remove_webhook", AsyncMock()) as mock_remove:
        response = await test_client.get("/bot/del")
        assert response.status_code == 200
        mock_remove.assert_awaited_once()
