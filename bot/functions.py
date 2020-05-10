# -*- coding:utf-8 -*-
"""
The main functions used to work with the Telegram bot
"""

from bot import bot, msg, DEFAULT_PARSE_MODE, NOT_FOUND_MESSAGE
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


def bot_cmd_command(message: msg):
    """

    :param message:
    :return:
    """
    return message.text


def bot_cmd_start(message: msg):
    """

    :param message:
    :return:
    """
    bot.send_message(message.chat.id, "Loi!")


def bot_cmd_gle(message: msg):
    """

    :param message:
    :return:
    """

    list_of_arguments = extract_args(message.text)

    if list_of_arguments:
        user_request = list_of_arguments[0]
        result = translation_by_key(user_request)
        if result:
            message_text = result
        else:
            message_text = NOT_FOUND_MESSAGE % user_request
    else:
        message_text = "You need to specify the English word you would like to find."

    bot.send_message(message.chat.id, message_text, parse_mode=DEFAULT_PARSE_MODE)


def bot_cmd_log(message: msg) -> bool:
    """

    :param message:
    :return:
    """
    list_of_arguments = extract_args(message.text)

    if list_of_arguments:
        user_request = list_of_arguments[0]
        if check_loglan_word(message.chat.id, user_request):
            return True
        message_text = NOT_FOUND_MESSAGE % user_request
    else:
        message_text = "You need to specify the Loglan word you would like to find."
    bot.send_message(message.chat.id, message_text, parse_mode=DEFAULT_PARSE_MODE)
    return True


def check_loglan_word(uid: int, user_request: str) -> bool:
    """
    Обработчик слова на логлане
    :param uid: Telegram User ID
    :param user_request: User request
    :return: Boolean
    """
    words = word_by_name(user_request)
    if words:
        for word in words:
            for element in word.get_telegram_card():
                bot.send_message(uid, element, parse_mode=DEFAULT_PARSE_MODE)
        return True
    return False


def check_foreign_word(uid: int, user_request: str):
    """
    Обработчик иностранного слова
    :param uid: Telegram User ID
    :param user_request: User request
    :return: Boolean
    """
    translation = translation_by_key(user_request)
    if translation:
        bot.send_message(uid, translation, parse_mode=DEFAULT_PARSE_MODE)
        return True
    return False


def bot_text_messages_handler(message: msg) -> bool:
    """
    The main handler of user's text messages
    :param message:
    :return:
    """

    user_request = message.text[1:] if message.text[0] == "/" else message.text
    uid = message.chat.id

    if not check_loglan_word(uid, user_request) and not check_foreign_word(uid, user_request):
        message_text = NOT_FOUND_MESSAGE % user_request
        bot.send_message(uid, message_text, parse_mode=DEFAULT_PARSE_MODE)

    if message.text:
        from pprint import pprint
        pprint(message.__dict__)
        return True

    return False


if __name__ == "__main__":
    pass
