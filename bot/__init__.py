# -*- coding:utf-8 -*-
# pylint: disable=C0103, C0413

"""
Initializing telegram bot
"""

from os import environ
from telebot import TeleBot, types

TOKEN = environ["TELEGRAM_BOT_TOKEN"]
APP_SITE = environ["APP_SITE"]
EN = "en"
DEFAULT_LANGUAGE = EN
DEFAULT_PARSE_MODE = "HTML"
NOT_FOUND_MESSAGE = "Sorry, but nothing was found for <b>%s</b>."

bot = TeleBot(TOKEN)
admin = int(environ["TELEGRAM_ADMIN_ID"])

ikm = types.InlineKeyboardMarkup
ikb = types.InlineKeyboardButton
rkm = types.ReplyKeyboardMarkup
rkb = types.KeyboardButton
cbq = types.CallbackQuery
msg = types.Message
imp = types.InputMediaPhoto

keyboard_permanent_resize = {"one_time_keyboard": False, "resize_keyboard": True, }

from bot import commands
