"""Telegram AsyncTeleBot Instance Initialization"""

from __future__ import annotations

from telebot.async_telebot import AsyncTeleBot

from app.bot.telegram.constants import DEFAULT_PARSE_MODE, TOKEN

# Initialize AsyncTeleBot instance
bot = AsyncTeleBot(
    token=TOKEN if TOKEN else "123456:FAKE_TOKEN_FOR_TESTING",
    parse_mode=DEFAULT_PARSE_MODE,
)
