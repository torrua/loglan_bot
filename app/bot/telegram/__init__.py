"""Telegram Bot Module Package"""

from __future__ import annotations

# Import processor to register message and callback handlers on bot
from app.bot.telegram import processor  # noqa: F401
from app.bot.telegram.bot import bot
from app.bot.telegram.constants import (
    ADMIN,
    DEFAULT_PARSE_MODE,
    DEFAULT_STYLE,
    EN,
    MESSAGE_NOT_FOUND,
    MESSAGE_SPECIFY_ENGLISH_WORD,
    MESSAGE_SPECIFY_LOGLAN_WORD,
    MIN_NUMBER_OF_BUTTONS,
    RU,
    SEPARATOR,
    TOKEN,
    cbq,
    msg,
)

__all__ = [
    "ADMIN",
    "DEFAULT_PARSE_MODE",
    "DEFAULT_STYLE",
    "EN",
    "MESSAGE_NOT_FOUND",
    "MESSAGE_SPECIFY_ENGLISH_WORD",
    "MESSAGE_SPECIFY_LOGLAN_WORD",
    "MIN_NUMBER_OF_BUTTONS",
    "RU",
    "SEPARATOR",
    "TOKEN",
    "bot",
    "cbq",
    "msg",
]
