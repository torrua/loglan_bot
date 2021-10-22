# -*- coding:utf-8 -*-
"""
Telegram bot command functions
"""

from bot import bot, msg, ADMIN, EN, DEFAULT_PARSE_MODE, NOT_FOUND_MESSAGE
from config.model_user import User
from config.model_telegram import TelegramWord as Word
from bot.handlers.functions import check_loglan_word, extract_args


def bot_cmd_start(message: msg):
    """
    Handle start command
    :param message:
    :return:
    """
    bot.send_message(message.chat.id, "Loi!")
    text = "\n".join(sorted([
        f"{key}: {value}" for key, value in message.from_user.__dict__.items()]))
    bot.send_message(ADMIN, text)

    db_user = User.from_db_by(message)

    if db_user:
        db_user.settings.reset()
    else:
        new_user = User.create_from(message)
        new_user.save()
        new_user.add_default_settings()


def bot_cmd_gle(message: msg):
    """
    Handle command for english word
    :param message:
    :return:
    """

    arguments = extract_args(message.text)

    if arguments:
        user_request = arguments[0]
        result = Word.translation_by_key(request=user_request, language=EN)
        message_text = result if result else NOT_FOUND_MESSAGE % user_request

    else:
        message_text = "You need to specify the English word you would like to find."

    bot.send_message(
        chat_id=message.chat.id,
        text=message_text,
        parse_mode=DEFAULT_PARSE_MODE)


def bot_cmd_log(message: msg):
    """
    Handle command for loglan word
    :param message:
    :return:
    """
    arguments = extract_args(message.text)

    if arguments:
        user_request = arguments[0]
        if check_loglan_word(user_id=message.chat.id, request=user_request):
            return
        message_text = NOT_FOUND_MESSAGE % user_request
    else:
        message_text = "You need to specify the Loglan word you would like to find."

    bot.send_message(
        chat_id=message.chat.id,
        text=message_text,
        parse_mode=DEFAULT_PARSE_MODE)
