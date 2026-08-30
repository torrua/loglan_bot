"""Processing Inline Button Actions Received from Telegram Bot"""

from __future__ import annotations

from callbaker import info_from_callback

from app.bot.telegram.bot import bot
from app.bot.telegram.constants import cbq
from app.bot.telegram.keyboards import WordKeyboard
from app.bot.telegram.models import export_as_str
from app.bot.telegram.notifications import notify_admin_query
from app.bot.telegram.variables import Mark
from app.decorators import logging_time
from app.logger import log
from app.services.dictionary import DictionaryService


@logging_time
async def bib_cancel(call: cbq) -> None:
    """Handles the 'Cancel' / 'Close' inline button click."""
    if call.message:
        await notify_admin_query(call.from_user, "Closed card", query_type="Button Close")
        try:
            await bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception as exc:
            log.warning("Could not delete message on cancel: %s", exc)


@logging_time
async def bib_predy_send_card(call: cbq) -> None:
    """Handles clicking on a specific Loglan word button from a list."""
    if not call.data or not call.message:
        return

    info = info_from_callback(call.data)
    record_id = int(info.get(Mark.record_id, 0))
    if not record_id:
        return

    uid = call.message.chat.id
    word = await DictionaryService.get_word_by_id(word_id=record_id)
    if word:
        await notify_admin_query(
            call.from_user,
            f"Selected word: {word.name} (ID: {word.id})",
            query_type="Button Select",
        )
        await bot.send_message(
            chat_id=uid,
            text=export_as_str(word),
            reply_markup=WordKeyboard(word).keyboard_cpx(),
        )


@logging_time
async def bib_predy_kb_cpx_switcher(call: cbq) -> None:
    """Handles showing/hiding complex words or djifoa lists on an existing card."""
    if not call.data or not call.message:
        return

    info = info_from_callback(call.data)
    slice_start = int(info.pop(Mark.slice_start, 0))
    action = str(info.pop(Mark.action, ""))
    record_id = int(info.get(Mark.record_id, 0))

    if not record_id:
        return

    word = await DictionaryService.get_word_by_id(word_id=record_id)
    if not word:
        return

    keyboard = WordKeyboard(word).keyboard_cpx(action=action, slice_start=slice_start)

    try:
        await bot.edit_message_reply_markup(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=keyboard,
        )
    except Exception as exc:
        log.debug("Reply markup unchanged or edit error: %s", exc)
