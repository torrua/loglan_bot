# -*- coding:utf-8 -*-
# pylint: disable=C0103, C0413

"""
Initializing telegram bot
"""

from os import environ
from telebot import TeleBot, types
from config.postgres import app, db
from config.postgres.models import Word, Key, Definition
from config.postgres.model_base import t_connect_keys
from config.postgres import model_user

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
