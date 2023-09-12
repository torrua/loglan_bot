# -*- coding:utf-8 -*-
"""
Telegram telegram_bot messages functions
"""

from app.telegram_bot.bot import bot, msg
from app.telegram_bot.bot.handlers.commands import send_message_by_key
from app.telegram_bot.bot.models import TelegramWord as Word
from app.engine import Session


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
