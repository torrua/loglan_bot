# -*- coding:utf-8 -*-
"""
The main functions used to work with the Telegram bot
"""

from bot import bot, msg, EN, DEFAULT_PARSE_MODE, NOT_FOUND_MESSAGE
from bot.db_functions import word_by_name, translation_by_key
from config import log


def extract_args(arg: str) -> list:
    """
    The function returns a list of parameters passed to the bot with a command
    :param arg: full command text
    :return: list of parameters
    """
    arguments = arg.split()[1:]
    log.debug(str(arguments))
    return arguments


def bot_cmd_start(message: msg):
    """
    Handle start command
    :param message:
    :return:
    """
    bot.send_message(message.chat.id, "Loi!")


def bot_cmd_gle(message: msg):
    """
    Handle command for english word
    :param message:
    :return:
    """

    arguments = extract_args(message.text)

    if arguments:
        user_request = arguments[0]
        result = translation_by_key(request=user_request, language=EN)
        message_text = result if result else NOT_FOUND_MESSAGE % user_request

    else:
        message_text = "You need to specify the English word you would like to find."

    bot.send_message(
        chat_id=message.chat.id,
        text=message_text,
        parse_mode=DEFAULT_PARSE_MODE)


def bot_cmd_log(message: msg) -> bool:
    """
    Handle command for loglan word
    :param message:
    :return:
    """
    arguments = extract_args(message.text)

    if arguments:
        user_request = arguments[0]
        if check_loglan_word(user_id=message.chat.id, request=user_request):
            return True
        message_text = NOT_FOUND_MESSAGE % user_request
    else:
        message_text = "You need to specify the Loglan word you would like to find."
    bot.send_message(
        chat_id=message.chat.id,
        text=message_text,
        parse_mode=DEFAULT_PARSE_MODE)
    return True


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


def bot_text_messages_handler(message: msg) -> None:
    """
    Handle user's text messages
    :param message:
    :return: None
    """

    user_request = message.text[1:] if message.text[0] == "/" else message.text
    uid = message.chat.id

    if not check_loglan_word(user_id=uid, request=user_request) and \
            not check_foreign_word(user_id=uid, request=user_request):

        bot.send_message(
            chat_id=uid,
            text=NOT_FOUND_MESSAGE % user_request,
            parse_mode=DEFAULT_PARSE_MODE, )


if __name__ == "__main__":
    pass
