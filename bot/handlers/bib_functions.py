# -*- coding: utf-8 -*-
"""Processing inline buttons calls received from telegram bot"""

from callbaker import info_from_callback
from telebot.apihelper import ApiException as TelebotApiException

from bot import bot, cbq
from bot.handlers.functions import check_loglan_word
from config.postgres.models import Word
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
    check_loglan_word(uid, info[mark_record_id])


def bib_predy_kb_cpx_switcher(call: cbq, state: bool):
    info = info_from_callback(call.data)
    slice_start = info.pop(mark_slice_start, 0)
    word = Word.query.filter(Word.id == info[mark_record_id]).first()
    kb = word.keyboard_cpx(show_list=state, slice_start=slice_start)

    bot.edit_message_reply_markup(
        chat_id=call.from_user.id,
        message_id=call.message.message_id,
        reply_markup=kb)


def bib_predy_kb_cpx_show(call: cbq):
    bib_predy_kb_cpx_switcher(call, True)


def bib_predy_kb_cpx_hide(call: cbq):
    bib_predy_kb_cpx_switcher(call, False)
