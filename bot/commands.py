"""
Модуль обработки команд, поступающих через телеграм-бота
"""

from bot import bot, msg, cbq
from bot.functions import bot_callback_inline, bot_text_messages_handler,\
    bot_cmd_start, bot_cmd_gle, bot_cmd_log
from bot.variables import t


@bot.message_handler(commands=["start"])
def command_start(message: msg):
    """
    Обработка команды /start
    :param message: Входяшее сообщение
    :return:
    """
    bot_cmd_start(message)


@bot.message_handler(commands=["gle"])
def command_english_word(message: msg):
    """
    Обработка команды /gle
    :param message: Входяшее сообщение
    :return:
    """
    bot_cmd_gle(message)


@bot.message_handler(commands=["log"])
def command_loglan_word(message: msg):
    """
    Обработка команды /log
    :param message: Входяшее сообщение
    :return:
    """
    bot_cmd_log(message)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call: cbq):
    """
    Все нажатия inline кнопок подадают на обработку в эту функцию.
    :param call: Входяший инлайн запрос
    :return:
    """
    bot_callback_inline(call)


@bot.message_handler(regexp="/[a-z]+")
@bot.message_handler(func=lambda message: True, content_types=[t])
def cpx_messages_handler(message: msg):
    """
    Весь поступающий боту текст попадает на обработку в эту функцию.
    :param message: Входяшее сообщение
    :return:
    """
    bot_text_messages_handler(message)
