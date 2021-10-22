# -*- coding:utf-8 -*-
"""
Telegram bot messages functions
"""

from bot import bot, DEFAULT_PARSE_MODE, msg, MESSAGE_NOT_FOUND
from bot.handlers.functions import check_foreign_word
from config.model_telegram import TelegramWord as Word


def bot_text_messages_handler(message: msg) -> None:
    """
    Handle user's text messages
    :param message:
    :return: None
    """

    user_request = message.text[1:] if message.text[0] == "/" else message.text
    uid = message.chat.id

    if words := Word.by_request(user_request):
        for word in words:
            word.send_card_to_user(bot, uid, DEFAULT_PARSE_MODE)

    elif not (check_foreign_word(user_id=uid, request=user_request)):

        bot.send_message(
            chat_id=uid,
            text=MESSAGE_NOT_FOUND % user_request,
            parse_mode=DEFAULT_PARSE_MODE, )
