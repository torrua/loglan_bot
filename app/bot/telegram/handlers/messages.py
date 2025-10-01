# -*- coding:utf-8 -*-
"""
Telegram bot messages functions
"""
from loglan_core import WordSelector

from app.bot.telegram import msg
from app.bot.telegram.handlers.commands import (
    send_message_by_key,
    send_messages_with_words,
)
from app.engine import async_session_maker


async def bot_text_messages_handler(message: msg) -> None:
    """
    Handle user's text messages
    :param message:
    :return: None
    """

    user_request = message.text.removeprefix("/")
    async with async_session_maker() as session:

        words = await (
            WordSelector()
            .by_name(user_request)
            .with_relationships()
            .all_async(session, unique=True)
        )

    if words:
        await send_messages_with_words(message, words)
    else:
        await send_message_by_key(user_request, message.chat.id)
