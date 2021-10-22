# -*- coding:utf-8 -*-
"""
Telegram bot common functions
"""

from bot import bot, DEFAULT_PARSE_MODE, DEFAULT_LANGUAGE
from config import log
from config.models import Word


def check_loglan_word(user_id: int, request: str) -> bool:
    """
    Handle loglan word
    :param user_id: Telegram User ID
    :param request: User request
    :return: Boolean
    """

    if isinstance(request, int):
        words = Word.query.filter(Word.id == request).all()
    else:
        words = Word.by_name(request).all()

    if not words:
        return False

    for word in words:
        bot.send_message(
            chat_id=user_id,
            text=word.export(),
            parse_mode=DEFAULT_PARSE_MODE,
            reply_markup=word.keyboard_cpx())
    return True


def check_foreign_word(user_id: int, request: str):
    """
    Handle foreign word
    :param user_id: Telegram User ID
    :param request: User request
    :return: Boolean
    """
    translation = Word.translation_by_key(request, DEFAULT_LANGUAGE)
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
