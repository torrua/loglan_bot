"""Telegram Bot Free-Text and Regex Message Handlers"""

from __future__ import annotations

from app.bot.telegram.constants import msg
from app.bot.telegram.handlers.commands import (
    send_message_by_key,
    send_messages_with_words,
)
from app.bot.telegram.notifications import notify_admin_query
from app.services.dictionary import DictionaryService


async def bot_text_messages_handler(message: msg) -> None:
    """Handles arbitrary text and slash-prefixed search requests."""
    if not message.text:
        return

    await notify_admin_query(
        getattr(message, "from_user", None), message.text, query_type="Text Query"
    )

    user_request = message.text.removeprefix("/").strip()
    if not user_request:
        return

    words = await DictionaryService.get_words_by_name(name=user_request)
    if words:
        await send_messages_with_words(message, words)
    else:
        await send_message_by_key(user_request, message.chat.id)
