# -*- coding:utf-8 -*-
"""
Telegram bot inline requests functions
"""
from callbaker import info_from_callback

from app.bot.telegram import cbq
from app.bot.telegram.handlers.bib_functions import bib_cancel
from app.bot.telegram.handlers.bib_functions import (
    bib_predy_send_card,
    bib_predy_kb_cpx_switcher,
)

from app.bot.telegram.variables import (
    Action,
    cancel,
    close,
    Mark,
    entity_predy,
)
from app.decorators import logging_time


@logging_time
async def bot_callback_inline(call: cbq):
    """
    Основной обработчик событий по нажатым inline кнопкам
    :param call:
    :return:
    """

    # Если сообщение из чата с ботом
    if call.data in [cancel, close]:
        await bib_cancel(call)  # no need to lang input
        return

    info = info_from_callback(call.data)
    current_entity = info.get(Mark.entity, None)
    current_action = info.get(Mark.action, None)

    if not (current_entity and current_action):
        return

    await entity_selector_general(call)


@logging_time
async def entity_selector_general(call: cbq):
    """
    :param call:
    :return:
    """
    info = info_from_callback(call.data)
    current_entity = info.get(Mark.entity, None)

    if current_entity == entity_predy:
        await action_selector_predy(call)


@logging_time
async def action_selector_predy(call: cbq):
    """
    :param call:
    :return:
    """
    info = info_from_callback(call.data)
    current_action = info.get(Mark.action, None)

    actions = {
        Action.send_card: bib_predy_send_card,
    }

    if action_to_run := actions.get(current_action, bib_predy_kb_cpx_switcher):
        await action_to_run(call)
