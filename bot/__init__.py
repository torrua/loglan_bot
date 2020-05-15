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

ikm = types.InlineKeyboardMarkup
ikb = types.InlineKeyboardButton
rkm = types.ReplyKeyboardMarkup
rkb = types.KeyboardButton
cbq = types.CallbackQuery
msg = types.Message
imp = types.InputMediaPhoto

keyboard_permanent_resize = {"one_time_keyboard": False, "resize_keyboard": True, }

from bot import processor
