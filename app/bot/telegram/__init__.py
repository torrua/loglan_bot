# -*- coding:utf-8 -*-
# pylint: disable=C0103, C0413

"""
Initializing telegram bot
"""
import os
from os import environ

from telebot import types
from telebot.async_telebot import AsyncTeleBot

EN, RU = "en", "ru"
DEFAULT_PARSE_MODE = "HTML"
MESSAGE_NOT_FOUND = "Sorry, but nothing was found for <b>%s</b>."
MESSAGE_SPECIFY_LOGLAN_WORD = (
    "You need to specify the Loglan word you would like to find."
)
MESSAGE_SPECIFY_ENGLISH_WORD = (
    "You need to specify the English word you would like to find."
)

MIN_NUMBER_OF_BUTTONS = 50
TOKEN = environ.get("TELEGRAM_BOT_TOKEN")
ADMIN = int(environ.get("TELEGRAM_ADMIN_ID"))
DEFAULT_STYLE = os.getenv("DEFAULT_STYLE", "ultra")
SEPARATOR = "@"

cbq = types.CallbackQuery
msg = types.Message

bot = AsyncTeleBot(TOKEN, parse_mode=DEFAULT_PARSE_MODE)

from app.bot.telegram import processor
