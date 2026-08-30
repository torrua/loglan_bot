"""Admin Query Notification Manager and Sender"""

from __future__ import annotations

import html
from typing import TYPE_CHECKING, Any

from app.bot.telegram.bot import bot
from app.bot.telegram.constants import ADMIN
from app.config import settings
from app.logger import log

if TYPE_CHECKING:
    from telebot import types


class AdminNotificationManager:
    """Manages admin notification toggles and state."""

    def __init__(self, initial_enabled: bool = True):
        self._enabled = initial_enabled

    @property
    def is_enabled(self) -> bool:
        return self._enabled

    def toggle(self) -> bool:
        self._enabled = not self._enabled
        return self._enabled

    def set_enabled(self, value: bool) -> None:
        self._enabled = value


# Singleton instance
admin_notifications = AdminNotificationManager(initial_enabled=settings.admin_notify_queries)


async def notify_admin_query(
    user: types.User | Any,
    query: str,
    query_type: str = "Search",
) -> None:
    """Sends a notification to the administrator about a user query if enabled."""
    if not admin_notifications.is_enabled or not ADMIN or not user:
        return

    user_id = getattr(user, "id", None)
    if user_id is None or user_id == ADMIN:
        return

    username = getattr(user, "username", None)
    first_name = getattr(user, "first_name", "") or ""
    last_name = getattr(user, "last_name", "") or ""
    full_name = f"{first_name} {last_name}".strip() or "User"

    user_label = f"@{username}" if username else f"ID: {user_id}"
    safe_query = html.escape(query.strip())

    notification_text = (
        f"🔔 <b>User Query</b> [<i>{html.escape(query_type)}</i>]\n"
        f"👤 {html.escape(full_name)} ({html.escape(user_label)}, ID: <code>{user_id}</code>)\n"
        f"📝 <code>{safe_query}</code>"
    )

    try:
        await bot.send_message(
            chat_id=ADMIN,
            text=notification_text,
        )
    except Exception as exc:
        log.warning("Could not send admin query notification: %s", exc)
