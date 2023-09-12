# -*- coding:utf-8 -*-
"""
Telegram telegram_bot inline requests functions
"""
from callbaker import info_from_callback

from app.telegram_bot.bot import cbq
from app.telegram_bot.bot.handlers.bib_functions import bib_cancel
from app.telegram_bot.bot.handlers.bib_functions import (
    bib_predy_send_card,
    bib_predy_kb_cpx_hide,
    bib_predy_kb_cpx_show,
)
from app.decorators import logging_time

from app.telegram_bot.bot.variables import (
    action_predy_send_card,
    action_predy_kb_cpx_hide,
    action_predy_kb_cpx_show,
)
from app.telegram_bot.bot.variables import cancel, close, mark_entity, mark_action, entity_predy


@logging_time
def bot_callback_inline(call: cbq):
    """
    Основной обработчик событий по нажатым inline кнопкам
    :param call:
    :return:
    """

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


@logging_time
def entity_selector_general(call: cbq):
    """
    :param call:
    :return:
    """
    info = info_from_callback(call.data)
    current_entity = info.get(mark_entity, None)

    if current_entity == entity_predy:
        action_selector_predy(call)


@logging_time
def action_selector_predy(call: cbq):
    """
    :param call:
    :return:
    """
    info = info_from_callback(call.data)
    current_action = info.get(mark_action, None)

    actions = {
        action_predy_send_card: bib_predy_send_card,
        action_predy_kb_cpx_hide: bib_predy_kb_cpx_hide,
        action_predy_kb_cpx_show: bib_predy_kb_cpx_show,
    }

    if action_to_run := actions.get(current_action):
        action_to_run(call)