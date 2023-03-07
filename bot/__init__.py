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
MESSAGE_NOT_FOUND = "Sorry, but nothing was found for <b>%s</b>."
MESSAGE_SPECIFY_LOGLAN_WORD = (
    "You need to specify the Loglan word you would like to find."
)
MESSAGE_SPECIFY_ENGLISH_WORD = (
    "You need to specify the English word you would like to find."
)

MIN_NUMBER_OF_BUTTONS = 50

bot = TeleBot(TOKEN, parse_mode=DEFAULT_PARSE_MODE)
ADMIN = int(environ.get("TELEGRAM_ADMIN_ID"))

cbq = types.CallbackQuery
msg = types.Message

from bot import processor
