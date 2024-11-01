# -*- coding:utf-8 -*-
"""
Telegram bot messages functions
"""
from loglan_core import WordSelector

from app.bot.telegram import bot, msg
from app.bot.telegram.handlers.commands import send_message_by_key
from app.bot.telegram.keyboards import WordKeyboard
from app.bot.telegram.models import export_as_str
from app.engine import Session


async def bot_text_messages_handler(message: msg) -> None:
    """
    Handle user's text messages
    :param message:
    :return: None
    """

    user_request = message.text.removeprefix("/")
    with Session() as session:

        words = (
            WordSelector()
            .by_name(user_request)
            .with_relationships()
            .all(session, unique=True)
        )

    if words:
        for word in words:
            await bot.send_message(
                chat_id=message.chat.id,
                text=export_as_str(word),
                reply_markup=WordKeyboard(word).keyboard_cpx(),
            )
    else:
        await send_message_by_key(user_request, message.chat.id)
