# -*- coding: utf-8 -*-
"""Processing commands received from telegram bot"""

from bot import bot, msg
from bot.handlers.commands import bot_cmd_start, bot_cmd_gle, bot_cmd_log
from bot.handlers.messages import bot_text_messages_handler
from config.postgres import app


@bot.message_handler(commands=["start"])
def command_start(message: msg):
    """
    Handle command /start
    :param message:
    :return:
    """
    with app.app_context():
        bot_cmd_start(message)


@bot.message_handler(commands=["g", "e", ])
def command_gleci(message: msg):
    """
    Handle command /gleci
    :param message:
    :return:
    """
    with app.app_context():
        bot_cmd_gle(message)


@bot.message_handler(commands=["l", ])
def command_logli(message: msg):
    """
    Handle command /logli
    :param message:
    :return:
    """
    with app.app_context():
        bot_cmd_log(message)


@bot.message_handler(regexp="/[a-z]+")
@bot.message_handler(func=lambda message: True, content_types=["text"])
def cpx_messages_handler(message: msg):
    """
    All text requests to the bot are processed by this function
    :param message:
    :return:
    """
    with app.app_context():
        bot_text_messages_handler(message)
