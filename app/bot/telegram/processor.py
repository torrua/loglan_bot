# pylint: disable=R0401

"""Processing commands received from telegram bot"""

from app.bot.telegram import bot, msg, cbq
from app.bot.telegram.handlers.commands import bot_cmd_start, bot_cmd_gle, bot_cmd_log
from app.bot.telegram.handlers.inline import bot_callback_inline
from app.bot.telegram.handlers.messages import bot_text_messages_handler
from app.decorators import logging_time


@bot.message_handler(commands=["start"])
@logging_time
async def command_start(message: msg):
    """
    Handle command /start
    :param message:
    :return:
    """
    await bot_cmd_start(message)


@bot.message_handler(
    commands=[
        "g",
        "e",
        "gle",
        "gleci",
    ]
)
@logging_time
async def command_gleci(message: msg):
    """
    Handle command /gleci
    :param message:
    :return:
    """
    await bot_cmd_gle(message)


@bot.message_handler(
    commands=[
        "l",
        "log",
        "logli",
    ]
)
@logging_time
async def command_logli(message: msg):
    """
    Handle command /logli
    :param message:
    :return:
    """
    await bot_cmd_log(message)


@bot.message_handler(regexp="/[a-z]+")
@bot.message_handler(func=lambda message: True, content_types=["text"])
@logging_time
async def cpx_messages_handler(message: msg):
    """
    All text requests to the bot are processed by this function
    :param message:
    :return:
    """
    await bot_text_messages_handler(message)


@bot.callback_query_handler(func=lambda call: True)
@logging_time
async def callback_inline(call: cbq):
    """
    All inline requests are processed by this function
    :param call: Incoming inline request
    :return:
    """
    await bot_callback_inline(call)
