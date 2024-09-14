# -*- coding:utf-8 -*-
"""
Telegram bot messages functions
"""
from loglan_core import WordSelector

from app.bot.telegram import bot, msg
from app.bot.telegram.handlers.commands import send_message_by_key
from app.bot.telegram.models import TelegramWord as Word
from app.engine import Session


async def bot_text_messages_handler(message: msg) -> None:
    """
    Handle user's text messages
    :param message:
    :return: None
    """

    user_request = message.text.removeprefix("/")
    with Session() as session:
        if (
            words := WordSelector(Word)
            .by_name(user_request)
            .with_relationships()
            .all(session)
        ):
            for word in words:
                await word.send_card_to_user(bot, message.chat.id)
        else:
            await send_message_by_key(session, user_request, message.chat.id)
