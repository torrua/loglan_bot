"""
Telegram bot command functions
"""

from loglan_core import WordSelector

from app.bot.telegram import (
    bot,
    msg,
    ADMIN,
    EN,
    MESSAGE_NOT_FOUND,
    MESSAGE_SPECIFY_LOGLAN_WORD,
    MESSAGE_SPECIFY_ENGLISH_WORD,
)
from app.bot.telegram.keyboards import kb_close, WordKeyboard
from app.bot.telegram.models import translation_by_key, export_as_str
from app.decorators import logging_time
from app.engine import async_session_maker


@logging_time
async def send_message_by_key(user_request: str, user_id: int):
    """
    :param user_request:
    :param user_id:
    :return:
    """
    words_found = await translation_by_key(
        request=user_request.lower(),
        language=EN,
    )
    reply = f"<b>{user_request}:</b>\n\n{words_found}"

    await bot.send_message(
        chat_id=user_id,
        text=reply if words_found else MESSAGE_NOT_FOUND % user_request,
        reply_markup=kb_close() if words_found else None,
    )


@logging_time
async def bot_cmd_start(message: msg):
    """
    Handle start command
    :param message:
    :return:
    """
    await bot.send_message(message.chat.id, "Loi!")
    new_user_info = "\n".join(
        sorted(
            [
                f"{key}: <b>{value}</b>"
                for key, value in message.from_user.__dict__.items()
                if value
            ]
        )
    )
    await bot.send_message(ADMIN, new_user_info)


@logging_time
async def bot_cmd_gle(message: msg):
    """
    Handle command for english word
    :param message:
    :return:
    """

    if not (arguments := message.text.split()[1:]):
        await bot.send_message(
            chat_id=message.chat.id,
            text=MESSAGE_SPECIFY_ENGLISH_WORD,
        )
        return

    user_request = arguments[0]

    await send_message_by_key(user_request, message.chat.id)


@logging_time
async def bot_cmd_log(message: msg):
    """
    Handle command for loglan word
    :param message:
    :return:
    """

    if not (arguments := message.text.split()[1:]):
        return await bot.send_message(
            chat_id=message.chat.id,
            text=MESSAGE_SPECIFY_LOGLAN_WORD,
        )

    async with async_session_maker() as session:
        words = await (
            WordSelector()
            .by_name(arguments[0])
            .with_relationships()
            .all_async(session, unique=True)
        )
    if not words:
        return await bot.send_message(
            chat_id=message.chat.id,
            text=MESSAGE_NOT_FOUND % arguments[0],
        )

    for word in words:
        await bot.send_message(
            chat_id=message.chat.id,
            text=export_as_str(word),
            reply_markup=WordKeyboard(word).keyboard_cpx(),
        )
