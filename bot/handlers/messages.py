# -*- coding:utf-8 -*-
"""
Telegram bot messages functions
"""

from bot import bot, DEFAULT_PARSE_MODE, msg, MESSAGE_NOT_FOUND, DEFAULT_LANGUAGE
from config.model_telegram import TelegramWord as Word


def bot_text_messages_handler(message: msg) -> None:
    """
    Handle user's text messages
    :param message:
    :return: None
    """

    user_request = message.text.removeprefix("/")

    if words := Word.by_request(user_request):
        for word in words:
            word.send_card_to_user(bot, message.chat.id, DEFAULT_PARSE_MODE)

    elif translation := Word.translation_by_key(user_request, DEFAULT_LANGUAGE):
        bot.send_message(
            chat_id=message.chat.id,
            text=translation,
            parse_mode=DEFAULT_PARSE_MODE)

    else:
        bot.send_message(
            chat_id=message.chat.id,
            text=MESSAGE_NOT_FOUND % user_request,
            parse_mode=DEFAULT_PARSE_MODE, )
