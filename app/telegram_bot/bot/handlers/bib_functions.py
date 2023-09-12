# -*- coding: utf-8 -*-
"""Processing inline buttons calls received from telegram telegram_bot"""

from callbaker import info_from_callback

from app.telegram_bot.bot import bot, cbq
from app.decorators import logging_time
from app.telegram_bot.bot.models import TelegramWord as Word
from app.engine import Session
from app.telegram_bot.bot.variables import mark_record_id, mark_slice_start


@logging_time
def bib_cancel(call: cbq):
    """
    Обработка нажатия кнопки 'Отмена'
    :param call:
    :return:
    """
    bot.delete_message(call.message.chat.id, call.message.message_id)


@logging_time
def bib_predy_send_card(call: cbq):
    """
    Обработка нажатия кнопки со словом на логлане
    :param call:
    :return:
    """
    info = info_from_callback(call.data)
    uid = call.message.chat.id
    with Session() as session:
        words = Word.by_request(session, info[mark_record_id])
        for word in words:
            word.send_card_to_user(session, bot, uid)


@logging_time
def bib_predy_kb_cpx_switcher(call: cbq, state: bool):
    """
    Обработка нажатия кнопки отображения/скрытия комплексных слов
    :param call:
    :param state:
    :return:
    """
    info = info_from_callback(call.data)
    slice_start = info.pop(mark_slice_start, 0)

    with Session() as session:
        word = Word.get_by_id(session, info[mark_record_id])
        keyboard = word.keyboard_cpx(show_list=state, slice_start=slice_start)

    bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        reply_markup=keyboard,
    )


@logging_time
def bib_predy_kb_cpx_show(call: cbq):
    """
    Обработка нажатия кнопки отображения комплексных слов
    :param call:
    :return:
    """
    bib_predy_kb_cpx_switcher(call, True)


@logging_time
def bib_predy_kb_cpx_hide(call: cbq):
    """
    Обработка нажатия кнопки скрытия комплексных слов
    :param call:
    :return:
    """
    bib_predy_kb_cpx_switcher(call, False)
