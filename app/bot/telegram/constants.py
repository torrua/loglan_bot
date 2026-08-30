"""Constants and Type Aliases for Telegram Bot"""

from __future__ import annotations

from telebot import types

from app.config import settings

# Language and formatting
EN: str = "en"
RU: str = "ru"
DEFAULT_PARSE_MODE: str = "HTML"
SEPARATOR: str = "@"
DEFAULT_STYLE: str = settings.default_style
MIN_NUMBER_OF_BUTTONS: int = 50

# Predefined messages
MESSAGE_NOT_FOUND: str = "Sorry, but nothing was found for <b>%s</b>."
MESSAGE_SPECIFY_LOGLAN_WORD: str = "You need to specify the Loglan word you would like to find."
MESSAGE_SPECIFY_ENGLISH_WORD: str = "You need to specify the English word you would like to find."

# Credentials
TOKEN: str = settings.telegram_bot_token
ADMIN: int | None = settings.telegram_admin_id

# Type aliases
cbq = types.CallbackQuery
msg = types.Message
