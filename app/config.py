"""Application Configuration Module"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load .env file from project root if it exists
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _str_to_bool(value: str | bool | None, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return value.strip().lower() in ("true", "1", "yes", "t", "y")


def _str_to_int(value: str | int | None, default: int | None = None) -> int | None:
    if value is None:
        return default
    if isinstance(value, int):
        return value
    try:
        return int(value.strip())
    except (ValueError, TypeError):
        return default


@dataclass(frozen=True)
class Settings:
    """Centralized typed application settings."""

    # Telegram Bot
    telegram_bot_token: str
    telegram_admin_id: int | None
    webhook_secret: str | None
    webhook_host: str | None
    admin_notify_queries: bool

    # Database
    database_url: str
    sql_echo: bool

    # UI / Language Defaults
    default_style: str
    default_search_language: str
    default_html_style: str

    # Server
    host: str
    port: int
    debug: bool

    @classmethod
    def load_from_env(cls) -> Settings:
        token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        admin_id = _str_to_int(os.getenv("TELEGRAM_ADMIN_ID"))
        webhook_secret = os.getenv("WEBHOOK_SECRET")
        webhook_host = os.getenv("WEBHOOK_HOST")
        admin_notify_queries = _str_to_bool(os.getenv("ADMIN_NOTIFY_QUERIES"), default=True)

        db_url = os.getenv("LOD_DATABASE_URL", "").strip()
        if not db_url:
            # Fallback for local development or testing if needed
            db_url = "sqlite+aiosqlite:///:memory:"

        sql_echo = _str_to_bool(os.getenv("SQL_REQUESTS_ECHO"), default=False)

        default_style = os.getenv("DEFAULT_STYLE", "ultra").strip()
        default_search_language = os.getenv("DEFAULT_SEARCH_LANGUAGE", "log").strip()
        default_html_style = os.getenv("DEFAULT_HTML_STYLE", "normal").strip()

        host = os.getenv("HOST", "0.0.0.0").strip()
        port = _str_to_int(os.getenv("PORT"), default=8080) or 8080
        debug = _str_to_bool(os.getenv("DEBUG"), default=False)

        return cls(
            telegram_bot_token=token,
            telegram_admin_id=admin_id,
            webhook_secret=webhook_secret,
            webhook_host=webhook_host,
            admin_notify_queries=admin_notify_queries,
            database_url=db_url,
            sql_echo=sql_echo,
            default_style=default_style,
            default_search_language=default_search_language,
            default_html_style=default_html_style,
            host=host,
            port=port,
            debug=debug,
        )


# Global settings instance
settings = Settings.load_from_env()
