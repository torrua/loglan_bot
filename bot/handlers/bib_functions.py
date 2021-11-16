# -*- coding: utf-8 -*-
"""Processing inline buttons calls received from telegram bot"""

from callbaker import info_from_callback

from bot import bot, cbq, DEFAULT_PARSE_MODE
from config.model_telegram import TelegramWord as Word
from variables import mark_record_id, mark_slice_start


def bib_cancel(call: cbq):
    """
    Обработка нажатия кнопки 'Отмена'
    :param call:
    :return:
    """
    bot.delete_message(call.message.chat.id, call.message.message_id)


def bib_predy_send_card(call: cbq):
    """
    Обработка нажатия кнопки со словом на логлане
    :param call:
    :return:
    """
    info = info_from_callback(call.data)
    uid = call.message.chat.id

    words = Word.by_request(info[mark_record_id])
    for word in words:
        word.send_card_to_user(bot, uid, DEFAULT_PARSE_MODE)


def bib_predy_kb_cpx_switcher(call: cbq, state: bool):
    """
    Обработка нажатия кнопки отображения/скрытия комплексных слов
    :param call:
    :param state:
    :return:
    """
    info = info_from_callback(call.data)
    slice_start = info.pop(mark_slice_start, 0)
    word = Word.get_by_id(info[mark_record_id])
    keyboard = word.keyboard_cpx(show_list=state, slice_start=slice_start)

    bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        reply_markup=keyboard,
    )


def bib_predy_kb_cpx_show(call: cbq):
    """
    Обработка нажатия кнопки отображения комплексных слов
    :param call:
    :return:
    """
    bib_predy_kb_cpx_switcher(call, True)


def bib_predy_kb_cpx_hide(call: cbq):
    """
    Обработка нажатия кнопки скрытия комплексных слов
    :param call:
    :return:
    """
    bib_predy_kb_cpx_switcher(call, False)
