# -*- coding:utf-8 -*-
"""
Telegram bot command functions
"""

from bot import bot, msg, ADMIN, EN, \
    MESSAGE_NOT_FOUND, MESSAGE_SPECIFY_LOGLAN_WORD, MESSAGE_SPECIFY_ENGLISH_WORD
from config.model_telegram import TelegramWord as Word
from engine import Session
from bot.decorators import logging_time
from config.model_telegram import kb_close


@logging_time
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


@logging_time
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

    with Session() as session:
        send_message_by_key(session, user_request, message.chat.id)

@logging_time
def send_message_by_key(session, user_request: str, user_id: str|int) -> None:
    """
    :param session:
    :param user_request:
    :param user_id:
    :return:
    """
    words_found = Word.translation_by_key(session=session, request=user_request.lower(), language=EN)
    reply = f"<b>{user_request}:</b>\n\n{words_found}"

    bot.send_message(
        chat_id=user_id,
        text=reply if words_found else MESSAGE_NOT_FOUND % user_request,
        reply_markup=kb_close() if words_found else None,
    )


@logging_time
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

    with Session() as session:
        if not (words := Word.by_request(session=session, request=arguments[0])):
            bot.send_message(
                chat_id=message.chat.id,
                text=MESSAGE_NOT_FOUND % arguments[0],
            )
            return

        for word in words:
            word.send_card_to_user(session=session, bot=bot, user_id=message.chat.id)
