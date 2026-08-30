"""Telegram Bot Handler Registrations"""

from __future__ import annotations

from app.bot.telegram.bot import bot
from app.bot.telegram.constants import cbq, msg
from app.bot.telegram.handlers.commands import (
    bot_cmd_gle,
    bot_cmd_log,
    bot_cmd_spy,
    bot_cmd_start,
)
from app.bot.telegram.handlers.inline import bot_callback_inline
from app.bot.telegram.handlers.messages import bot_text_messages_handler
from app.decorators import logging_time


@bot.message_handler(commands=["start"])
@logging_time
async def command_start(message: msg) -> None:
    """Handle /start command."""
    await bot_cmd_start(message)


@bot.message_handler(commands=["spy", "admin_spy", "notify"])
@logging_time
async def command_spy(message: msg) -> None:
    """Handle admin query notifications toggle command."""
    await bot_cmd_spy(message)


@bot.message_handler(commands=["g", "e", "gle", "gleci"])
@logging_time
async def command_gleci(message: msg) -> None:
    """Handle English translation commands (/gle, /gleci, /g, /e)."""
    await bot_cmd_gle(message)


@bot.message_handler(commands=["l", "log", "logli"])
@logging_time
async def command_logli(message: msg) -> None:
    """Handle Loglan translation commands (/log, /logli, /l)."""
    await bot_cmd_log(message)


@bot.message_handler(regexp="/[a-z]+")
@bot.message_handler(func=lambda message: True, content_types=["text"])
@logging_time
async def cpx_messages_handler(message: msg) -> None:
    """Handle all other text search requests."""
    await bot_text_messages_handler(message)


@bot.callback_query_handler(func=lambda call: True)
@logging_time
async def callback_inline(call: cbq) -> None:
    """Handle all inline keyboard callback queries."""
    await bot_callback_inline(call)
