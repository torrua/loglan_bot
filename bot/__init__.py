# -*- coding:utf-8 -*-
# pylint: disable=C0103, C0413

"""
Initializing telegram bot
"""

from os import environ
from telebot import TeleBot, types
from app.model_dictionary import Word, Key, Definition, t_connect_keys

TOKEN = environ.get("TELEGRAM_BOT_TOKEN")
APP_SITE = environ.get("APP_SITE")
EN = "en"
DEFAULT_LANGUAGE = environ.get("DEFAULT_LANGUAGE", EN)
DEFAULT_PARSE_MODE = "HTML"
NOT_FOUND_MESSAGE = "Sorry, but nothing was found for <b>%s</b>."

bot = TeleBot(TOKEN)
ADMIN = int(environ.get("TELEGRAM_ADMIN_ID"))

cbq = types.CallbackQuery
msg = types.Message

from bot import processor
