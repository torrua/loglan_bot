# -*- coding: utf-8 -*-
# pylint: disable=R0401

"""Processing commands received from telegram bot"""

from bot import bot, msg, cbq
from bot.handlers.commands import bot_cmd_start, bot_cmd_gle, bot_cmd_log
from bot.handlers.messages import bot_text_messages_handler
from bot.handlers.inline import bot_callback_inline
from config import app


@bot.message_handler(commands=["start"])
def command_start(message: msg):
    """
    Handle command /start
    :param message:
    :return:
    """
    with app.app_context():
        bot_cmd_start(message)


@bot.message_handler(
    commands=[
        "g",
        "e",
        "gleci",
    ]
)
def command_gleci(message: msg):
    """
    Handle command /gleci
    :param message:
    :return:
    """
    with app.app_context():
        bot_cmd_gle(message)


@bot.message_handler(
    commands=[
        "l",
        "logli",
    ]
)
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


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: cbq):
    """
    All inline requests are processed by this function
    :param call: Incoming inline request
    :return:
    """
    with app.app_context():
        bot_callback_inline(call)
