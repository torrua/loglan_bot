# -*- coding:utf-8 -*-
"""
Модуль с инициирующими данными телеграм-бота
"""
# pylint: disable=C0103, C0413

from os import environ
from telebot import TeleBot, types
from app.models import Word, Key, Definition, t_connect_keys

TOKEN = environ["TELEGRAM_BOT_TOKEN"]
APP_SITE = environ["APP_SITE"]

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
