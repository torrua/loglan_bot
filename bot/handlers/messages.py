# -*- coding:utf-8 -*-
"""
Telegram bot messages functions
"""

from bot import bot, msg
from bot.handlers.commands import send_message_by_key
from config.model_telegram import TelegramWord as Word
from engine import Session


def bot_text_messages_handler(message: msg) -> None:
    """
    Handle user's text messages
    :param message:
    :return: None
    """

    user_request = message.text.removeprefix("/")
    with Session() as session:
        if words := Word.by_request(session, user_request):
            for word in words:
                word.send_card_to_user(session, bot, message.chat.id)
        else:
            send_message_by_key(session, user_request, message.chat.id)
