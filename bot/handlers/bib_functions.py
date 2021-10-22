# -*- coding: utf-8 -*-
"""Processing inline buttons calls received from telegram bot"""

from callbaker import info_from_callback
from telebot.apihelper import ApiException as TelebotApiException

from bot import bot, cbq, DEFAULT_PARSE_MODE
from config.model_telegram import TelegramWord as Word
from variables import mark_record_id, mark_slice_start


def bib_cancel(call: cbq) -> bool:
    """
    Дополнительные меню: обработка нажатия кнопки 'Отмена'
    :param call:
    :return:
    """
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except TelebotApiException:
        return False
    else:
        return True


def bib_predy_send_card(call: cbq):
    info = info_from_callback(call.data)
    uid = call.message.chat.id

    words = Word.by_request(info[mark_record_id])
    for word in words:
        word.send_card_to_user(bot, uid, DEFAULT_PARSE_MODE)


def bib_predy_kb_cpx_switcher(call: cbq, state: bool):
    info = info_from_callback(call.data)
    slice_start = info.pop(mark_slice_start, 0)
    word = Word.get_by_id(info[mark_record_id])
    kb = word.keyboard_cpx(show_list=state, slice_start=slice_start)

    bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        reply_markup=kb)


def bib_predy_kb_cpx_show(call: cbq):
    bib_predy_kb_cpx_switcher(call, True)


def bib_predy_kb_cpx_hide(call: cbq):
    bib_predy_kb_cpx_switcher(call, False)
