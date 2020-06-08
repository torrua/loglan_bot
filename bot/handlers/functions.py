# -*- coding:utf-8 -*-
"""
Telegram bot common functions
"""

from bot import bot, DEFAULT_PARSE_MODE
from bot.functions_dictionary_db import word_by_name, translation_by_key
from config import log


def check_loglan_word(user_id: int, request: str) -> bool:
    """
    Handle loglan word
    :param user_id: Telegram User ID
    :param request: User request
    :return: Boolean
    """
    words = word_by_name(request)
    if not words:
        return False

    for word in words:
        for element in word.export():
            bot.send_message(
                chat_id=user_id,
                text=element,
                parse_mode=DEFAULT_PARSE_MODE)
    return True


def check_foreign_word(user_id: int, request: str):
    """
    Handle foreign word
    :param user_id: Telegram User ID
    :param request: User request
    :return: Boolean
    """
    translation = translation_by_key(request)
    if translation:
        bot.send_message(
            chat_id=user_id,
            text=translation,
            parse_mode=DEFAULT_PARSE_MODE)
        return True
    return False


def extract_args(arg: str) -> list:
    """
    The function returns a list of parameters passed to the bot with a command
    :param arg: full command text
    :return: list of parameters
    """
    arguments = arg.split()[1:]
    log.debug(str(arguments))
    return arguments