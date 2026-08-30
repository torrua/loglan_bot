"""Tests for application settings and configuration"""

import os
from unittest.mock import patch

from app.config import Settings, _str_to_bool, _str_to_int


def test_str_to_bool():
    assert _str_to_bool("true") is True
    assert _str_to_bool("1") is True
    assert _str_to_bool("yes") is True
    assert _str_to_bool("false") is False
    assert _str_to_bool("0") is False
    assert _str_to_bool("no") is False
    assert _str_to_bool(None, default=True) is True
    assert _str_to_bool(True) is True


def test_str_to_int():
    assert _str_to_int("123") == 123
    assert _str_to_int(" 456 ") == 456
    assert _str_to_int("invalid", default=999) == 999
    assert _str_to_int(None, default=10) == 10
    assert _str_to_int(42) == 42


def test_settings_defaults():
    with patch.dict(os.environ, {}, clear=True):
        s = Settings.load_from_env()
        assert s.telegram_bot_token == ""
        assert s.telegram_admin_id is None
        assert s.default_style == "ultra"
        assert s.default_search_language == "log"
        assert s.default_html_style == "normal"
        assert s.port == 8080
        assert s.debug is False


def test_settings_custom():
    custom_env = {
        "TELEGRAM_BOT_TOKEN": "custom_token_123",
        "TELEGRAM_ADMIN_ID": "987654",
        "DEFAULT_STYLE": "normal",
        "PORT": "9000",
        "DEBUG": "true",
        "LOD_DATABASE_URL": "postgresql+asyncpg://user:pass@host/db",
    }
    with patch.dict(os.environ, custom_env, clear=True):
        s = Settings.load_from_env()
        assert s.telegram_bot_token == "custom_token_123"
        assert s.telegram_admin_id == 987654
        assert s.default_style == "normal"
        assert s.port == 9000
        assert s.debug is True
        assert s.database_url == "postgresql+asyncpg://user:pass@host/db"
