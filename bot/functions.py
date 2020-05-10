# -*- coding:utf-8 -*-
"""
Основные функции, используемые для работы с Телеграм
"""

from telebot.apihelper import ApiException as TelebotApiException

from bot import bot, msg, cbq
from bot.db_functions import word_by_name, translation_by_key
from bot.variables import cancel, close
from config import log


def extract_args(arg: str) -> list:
    """
    Функця возвращает список параметров, переданных через пробел с коммандой боту
    :param arg: полный текст исходной команды
    :return: список параметров
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
    bot.send_message(message.chat.id, "Hello")


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
            message_text = "Sorry, but nothing was found for <b>%s</b>." % user_request
    else:
        message_text = "You need to specify the English word you would like to find."

    bot.send_message(message.chat.id, message_text, parse_mode="HTML")


def bot_cmd_log(message: msg) -> bool:
    """

    :param message:
    :return:
    """
    list_of_arguments = extract_args(message.text)

    if list_of_arguments:
        user_request = list_of_arguments[0]
        if handle_loglan_word(message.chat.id, user_request):
            return True
        message_text = "Sorry, but nothing was found for <b>%s</b>." % user_request
    else:
        message_text = "You need to specify the Loglan word you would like to find."
    bot.send_message(message.chat.id, message_text, parse_mode="HTML")
    return True


def handle_loglan_word(uid: int, user_request: str) -> bool:
    """
    Обработчик слова на логлане
    :param uid: Идентификационный номер пользователя в Телеграм
    :param user_request: Пользовательский запрос
    :return: Boolean
    """
    words = word_by_name(user_request)
    if words:
        for word in words:
            for element in word.get_telegram_card():
                bot.send_message(uid, element, parse_mode="HTML")
        return True
    return False


def handle_foreign_word(uid, user_request):
    """
    Обработчик иностранного слова
    :param uid: Идентификационный номер пользователя в Телеграм
    :param user_request: Пользовательский запрос
    :return: Boolean
    """
    translation = translation_by_key(user_request)
    if translation:
        bot.send_message(uid, translation, parse_mode="HTML")
        return True
    return False


def bot_callback_inline(call: cbq):
    """
    Основной обработчик событий по нажатым inline кнопкам
    :param call:
    :return:
    """
    # Если сообщение из чата с ботом
    if call.message:
        if call.data == cancel or call.data == close:
            bib_cancel(call)  # no need to lang input


def bot_text_messages_handler(message: msg) -> bool:
    """
    Основной обработчик текстовых сообщений пользователя
    :param message:
    :return:
    """

    user_request = message.text[1:] if message.text[0] == "/" else message.text
    uid = message.chat.id

    if not handle_loglan_word(uid, user_request) and not handle_foreign_word(uid, user_request):
        message_text = "Sorry, but nothing was found for <b>%s</b>." % user_request
        bot.send_message(uid, message_text, parse_mode="HTML")

    if message.text:
        from pprint import pprint
        pprint(message.__dict__)
        return True

    return False


def bib_cancel(call: cbq) -> bool:
    """
    Дополнительные меню: обработка нажатия кнопки 'Отмена'
    :param call:
    :return:
    """
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except TelebotApiException:
        return False
    else:
        return True


if __name__ == "__main__":
    pass
