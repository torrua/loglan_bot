"""Telegram Bot Inline Query and Callback Dispatcher"""

from __future__ import annotations

from callbaker import info_from_callback

from app.bot.telegram.constants import (
    cbq,
)
from app.bot.telegram.handlers.bib_functions import (
    bib_cancel,
    bib_predy_kb_cpx_switcher,
    bib_predy_send_card,
)
from app.bot.telegram.variables import (
    Action,
    Mark,
    cancel,
    close,
    entity_predy,
)
from app.decorators import logging_time


@logging_time
async def bot_callback_inline(call: cbq) -> None:
    """Main callback query dispatcher for inline button interactions."""
    if not call.data:
        return

    if call.data in (cancel, close):
        await bib_cancel(call)
        return

    info = info_from_callback(call.data)
    current_entity = info.get(Mark.entity)
    current_action = info.get(Mark.action)

    if not (current_entity and current_action):
        return

    await entity_selector_general(call)


@logging_time
async def entity_selector_general(call: cbq) -> None:
    """Routes callbacks based on entity type."""
    if not call.data:
        return

    info = info_from_callback(call.data)
    current_entity = info.get(Mark.entity)

    if current_entity == entity_predy:
        await action_selector_predy(call)


@logging_time
async def action_selector_predy(call: cbq) -> None:
    """Routes predy entity callbacks to specific handler functions."""
    if not call.data:
        return

    info = info_from_callback(call.data)
    current_action = info.get(Mark.action)

    actions = {
        Action.send_card: bib_predy_send_card,
    }

    action_to_run = actions.get(current_action, bib_predy_kb_cpx_switcher)
    await action_to_run(call)
