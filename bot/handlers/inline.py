# -*- coding:utf-8 -*-
"""
Telegram bot inline requests functions
"""
from callbaker import info_from_callback

from bot import cbq
from bot.handlers.bib_functions import bib_cancel
from bot.handlers.bib_functions import bib_predy_send_card, \
    bib_predy_kb_cpx_hide, bib_predy_kb_cpx_show
from config import log
from variables import action_predy_send_card, \
    action_predy_kb_cpx_hide, action_predy_kb_cpx_show
from variables import cancel, close, \
    mark_entity, mark_action, entity_predy


def bot_callback_inline(call: cbq):
    """
    Основной обработчик событий по нажатым inline кнопкам
    :param call:
    :return:
    """
    log.info("bot_callback_inline")
    # Если сообщение из чата с ботом

    if call.data in [cancel, close]:
        bib_cancel(call)  # no need to lang input
        return

    info = info_from_callback(call.data)
    current_entity = info.get(mark_entity, None)
    current_action = info.get(mark_action, None)

    if not (current_entity and current_action):
        return

    entity_selector_general(call)


def entity_selector_general(call: cbq):
    """
    :param call:
    :return:
    """
    log.info("entity_selector_general")
    info = info_from_callback(call.data)
    current_entity = info.get(mark_entity, None)

    if current_entity == entity_predy:
        action_selector_predy(call)


def action_selector_predy(call: cbq):
    """
    :param call:
    :return:
    """
    log.info("action_selector_predy")
    info = info_from_callback(call.data)
    current_action = info.get(mark_action, None)

    if current_action == action_predy_send_card:
        bib_predy_send_card(call)
    elif current_action == action_predy_kb_cpx_hide:
        bib_predy_kb_cpx_hide(call)
    elif current_action == action_predy_kb_cpx_show:
        bib_predy_kb_cpx_show(call)
