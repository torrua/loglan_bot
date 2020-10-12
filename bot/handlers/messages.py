# -*- coding:utf-8 -*-
"""
Telegram bot messages functions
"""

from bot import bot, DEFAULT_PARSE_MODE, msg, NOT_FOUND_MESSAGE
from bot.handlers.functions import check_loglan_word, check_foreign_word
from config.postgres import run_with_context


@run_with_context
def bot_text_messages_handler(message: msg) -> None:
    """
    Handle user's text messages
    :param message:
    :return: None
    """

    user_request = message.text[1:] if message.text[0] == "/" else message.text
    uid = message.chat.id

    if not (
        check_loglan_word(user_id=uid, request=user_request)
        or check_foreign_word(user_id=uid, request=user_request)
    ):

        bot.send_message(
            chat_id=uid,
            text=NOT_FOUND_MESSAGE % user_request,
            parse_mode=DEFAULT_PARSE_MODE, )
