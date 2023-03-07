# -*- coding:utf-8 -*-
"""
Telegram bot command functions
"""

from bot import bot, msg, ADMIN, EN, \
    MESSAGE_NOT_FOUND, MESSAGE_SPECIFY_LOGLAN_WORD, MESSAGE_SPECIFY_ENGLISH_WORD
from config.model_telegram import TelegramWord as Word
from app import Session


def bot_cmd_start(message: msg):
    """
    Handle start command
    :param message:
    :return:
    """
    bot.send_message(message.chat.id, "Loi!")
    new_user_info = "\n".join(sorted([
        f"{key}: <b>{value}</b>" for key, value in message.from_user.__dict__.items() if value]))
    bot.send_message(ADMIN, new_user_info)


def bot_cmd_gle(message: msg):
    """
    Handle command for english word
    :param message:
    :return:
    """

    if not (arguments := message.text.split()[1:]):
        bot.send_message(
            chat_id=message.chat.id,
            text=MESSAGE_SPECIFY_ENGLISH_WORD,
        )
        return

    user_request = arguments[0]
    result = Word.translation_by_key(session=Session, request=user_request, language=EN)
    bot.send_message(
        chat_id=message.chat.id,
        text=result if result else MESSAGE_NOT_FOUND % user_request,
    )


def bot_cmd_log(message: msg):
    """
    Handle command for loglan word
    :param message:
    :return:
    """

    if not (arguments := message.text.split()[1:]):
        bot.send_message(
            chat_id=message.chat.id,
            text=MESSAGE_SPECIFY_LOGLAN_WORD,
        )
        return

    if not (words := Word.by_request(request=arguments[0])):
        bot.send_message(
            chat_id=message.chat.id,
            text=MESSAGE_NOT_FOUND % arguments[0],
        )
        return

    for word in words:
        word.send_card_to_user(None, bot=bot, user_id=message.chat.id)
