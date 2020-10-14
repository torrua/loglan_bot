# -*- coding:utf-8 -*-
# pylint: disable=C0103, C0413

"""
Initializing telegram bot
"""

from os import environ
from telebot import TeleBot, types
from config import DEFAULT_LANGUAGE, EN

TOKEN = environ.get("TELEGRAM_BOT_TOKEN")
APP_SITE = environ.get("APP_SITE")
DEFAULT_PARSE_MODE = "HTML"
NOT_FOUND_MESSAGE = "Sorry, but nothing was found for <b>%s</b>."

bot = TeleBot(TOKEN)
ADMIN = int(environ.get("TELEGRAM_ADMIN_ID"))

cbq = types.CallbackQuery
msg = types.Message

from bot import processor
