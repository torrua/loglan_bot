# -*- coding:utf-8 -*-
"""
Telegram bot command functions
"""

from bot import bot, msg, ADMIN, EN, DEFAULT_PARSE_MODE, \
    MESSAGE_NOT_FOUND, MESSAGE_SPECIFY_LOGLAN_WORD, MESSAGE_SPECIFY_ENGLISH_WORD
from config.model_user import User
from config.model_telegram import TelegramWord as Word


def bot_cmd_start(message: msg):
    """
    Handle start command
    :param message:
    :return:
    """
    bot.send_message(message.chat.id, "Loi!")
    text = "\n".join(sorted([
        f"{key}: {value}" for key, value in message.from_user.__dict__.items()]))
    bot.send_message(ADMIN, text)

    db_user = User.from_db_by(message)

    if db_user:
        db_user.settings.reset()
    else:
        new_user = User.create_from(message)
        new_user.save()
        new_user.add_default_settings()


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
            parse_mode=DEFAULT_PARSE_MODE)
        return

    result = Word.translation_by_key(request=arguments[0], language=EN)
    bot.send_message(
        chat_id=message.chat.id,
        text=result if result else MESSAGE_NOT_FOUND % arguments[0],
        parse_mode=DEFAULT_PARSE_MODE)


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
            parse_mode=DEFAULT_PARSE_MODE)
        return

    if not (words := Word.by_request(arguments[0])):
        bot.send_message(
            chat_id=message.chat.id,
            text=MESSAGE_NOT_FOUND % arguments[0],
            parse_mode=DEFAULT_PARSE_MODE)
        return

    for word in words:
        word.send_card_to_user(
            bot=bot,
            user_id=message.chat.id,
            parse_mode=DEFAULT_PARSE_MODE)
