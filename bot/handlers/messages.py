# -*- coding:utf-8 -*-
"""
Telegram bot messages functions
"""

from bot import bot, msg, MESSAGE_NOT_FOUND, DEFAULT_LANGUAGE
from config.model_telegram import TelegramWord as Word
from app import Session


def bot_text_messages_handler(message: msg) -> None:
    """
    Handle user's text messages
    :param message:
    :return: None
    """

    user_request = message.text.removeprefix("/")

    if words := Word.by_request(Session, user_request):
        for word in words:
            word.send_card_to_user(Session, bot, message.chat.id)
    elif translation := Word.translation_by_key(Session, user_request, DEFAULT_LANGUAGE):
        bot.send_message(
            chat_id=message.chat.id,
            text=translation,
        )

    else:
        bot.send_message(
            chat_id=message.chat.id,
            text=MESSAGE_NOT_FOUND % user_request,
        )
