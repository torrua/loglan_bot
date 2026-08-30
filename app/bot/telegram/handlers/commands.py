"""Telegram Bot Command Handlers (/start, /gle, /log, /spy)"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from app.bot.telegram.bot import bot
from app.bot.telegram.constants import (
    ADMIN,
    EN,
    MESSAGE_NOT_FOUND,
    MESSAGE_SPECIFY_ENGLISH_WORD,
    MESSAGE_SPECIFY_LOGLAN_WORD,
    msg,
)
from app.bot.telegram.keyboards import WordKeyboard, kb_close
from app.bot.telegram.models import export_as_str, translation_by_key
from app.bot.telegram.notifications import admin_notifications, notify_admin_query
from app.decorators import logging_time
from app.logger import log
from app.services.dictionary import DictionaryService

if TYPE_CHECKING:
    from loglan_core import Word


@logging_time
async def send_message_by_key(user_request: str, user_id: int) -> None:
    """Finds words by foreign language key and sends formatted message."""
    words_found = await translation_by_key(
        request=user_request.lower(),
        language=EN,
    )
    reply = f"<b>{user_request}:</b>\n\n{words_found}"

    await bot.send_message(
        chat_id=user_id,
        text=reply if words_found else MESSAGE_NOT_FOUND % user_request,
        reply_markup=kb_close() if words_found else None,
    )


@logging_time
async def bot_cmd_start(message: msg) -> None:
    """Handles the /start command."""
    await bot.send_message(message.chat.id, "Loi!")

    if ADMIN and message.from_user:
        user_dict = message.from_user.__dict__
        new_user_info = "\n".join(sorted([f"{k}: <b>{v}</b>" for k, v in user_dict.items() if v]))
        try:
            await bot.send_message(ADMIN, new_user_info)
        except Exception as exc:
            log.warning("Failed to notify admin about new user: %s", exc)


@logging_time
async def bot_cmd_spy(message: msg) -> None:
    """Admin command to toggle or configure user query notifications (/spy, /spy on, /spy off)."""
    user = message.from_user
    if not ADMIN or not user or user.id != ADMIN:
        return

    text = (message.text or "").strip().lower()
    parts = text.split()

    if len(parts) > 1:
        action = parts[1]
        if action in ("on", "1", "true", "enable", "start"):
            admin_notifications.set_enabled(True)
        elif action in ("off", "0", "false", "disable", "stop"):
            admin_notifications.set_enabled(False)
        else:
            admin_notifications.toggle()
    else:
        admin_notifications.toggle()

    state_str = "включен (ON) 🔔" if admin_notifications.is_enabled else "выключен (OFF) 🔕"
    reply = (
        f"<b>Режим мониторинга запросов пользователей:</b> {state_str}\n\n"
        f"<i>Используйте <code>/spy on</code>, <code>/spy off</code> или просто <code>/spy</code> для переключения.</i>"
    )
    await bot.send_message(chat_id=message.chat.id, text=reply)


@logging_time
async def bot_cmd_gle(message: msg) -> None:
    """Handles English word search command (/gle, /gleci, /g, /e)."""
    if not message.text:
        return

    await notify_admin_query(getattr(message, "from_user", None), message.text, query_type="/gle")

    arguments = message.text.split()[1:]
    if not arguments:
        await bot.send_message(
            chat_id=message.chat.id,
            text=MESSAGE_SPECIFY_ENGLISH_WORD,
        )
        return

    user_request = arguments[0]
    await send_message_by_key(user_request, message.chat.id)


@logging_time
async def bot_cmd_log(message: msg) -> None:
    """Handles Loglan word search command (/log, /logli, /l)."""
    if not message.text:
        return

    await notify_admin_query(getattr(message, "from_user", None), message.text, query_type="/log")

    arguments = message.text.split()[1:]
    if not arguments:
        await bot.send_message(
            chat_id=message.chat.id,
            text=MESSAGE_SPECIFY_LOGLAN_WORD,
        )
        return

    target_word = arguments[0]
    words = await DictionaryService.get_words_by_name(name=target_word)
    if not words:
        await bot.send_message(
            chat_id=message.chat.id,
            text=MESSAGE_NOT_FOUND % target_word,
        )
        return

    await send_messages_with_words(message, words)


async def send_messages_with_words(message: msg, words: Sequence[Word]) -> None:
    """Sends individual formatted messages with inline keyboards for each word."""
    for word in words:
        await bot.send_message(
            chat_id=message.chat.id,
            text=export_as_str(word),
            reply_markup=WordKeyboard(word).keyboard_cpx(),
        )
