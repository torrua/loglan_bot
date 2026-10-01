"""Telegram WebApp authentication and HMAC-SHA256 verification."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import urllib.parse
from functools import wraps
from typing import Any

from quart import g, jsonify, request

from app.config import settings
from app.logger import log


def get_admin_ids() -> set[int]:
    """Retrieve allowed admin Telegram user IDs from settings or environment."""
    admins: set[int] = set()
    if settings.telegram_admin_id:
        admins.add(settings.telegram_admin_id)
    raw_env = os.getenv("ADMIN_IDS") or os.getenv("TELEGRAM_ADMIN_IDS")
    if raw_env:
        for p in raw_env.split(","):
            p = p.strip()
            if p.isdigit():
                admins.add(int(p))
    return admins


def get_bot_token() -> str:
    """Retrieve Telegram Bot Token from settings."""
    return settings.telegram_bot_token or ""


def _compute_hash(items: list[tuple[str, str]], bot_token: str) -> str:
    data_check_string = "\n".join(f"{k}={v}" for k, v in items)
    secret_key = hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()
    return hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()


def validate_init_data(
    init_data_raw: str,
    bot_token: str,
    ttl_seconds: int = 86400,
) -> tuple[bool, dict[str, Any] | None, str | None]:
    """
    Validates Telegram WebApp initData string using HMAC-SHA256 according to Telegram specifications.
    """
    if not init_data_raw:
        return False, None, "Missing initData"
    if not bot_token:
        return False, None, "Server missing BOT_TOKEN"

    try:
        parsed = dict(urllib.parse.parse_qsl(init_data_raw, keep_blank_values=True))
    except Exception as e:
        return False, None, f"Failed to parse initData: {e}"

    received_hash = parsed.pop("hash", None)
    auth_date_str = parsed.get("auth_date")
    if not received_hash or not auth_date_str:
        return False, None, "Missing hash or auth_date in initData"

    try:
        auth_date = int(auth_date_str)
    except ValueError:
        return False, None, "Invalid auth_date format"

    now = int(time.time())
    if now - auth_date > ttl_seconds:
        return False, None, f"initData expired (age: {now - auth_date}s > {ttl_seconds}s)"

    items = sorted(parsed.items(), key=lambda x: x[0])
    calculated_hash = _compute_hash(items, bot_token)

    if not hmac.compare_digest(calculated_hash.lower(), received_hash.lower()):
        return False, None, "Hash mismatch - invalid signature"

    user_info = None
    if "user" in parsed:
        try:
            user_info = json.loads(parsed["user"])
        except Exception:
            user_info = None

    payload = {
        "user": user_info,
        "auth_date": auth_date,
        "query_id": parsed.get("query_id"),
        "raw": parsed,
    }
    return True, payload, None


def extract_init_data() -> str:
    """Extract initData from request headers or query params."""
    # 1. Primary custom header
    header_val = request.headers.get("X-Telegram-Init-Data")
    if header_val:
        return header_val.strip()

    # 2. Authorization header: "tma <initData>"
    auth_header = request.headers.get("Authorization", "")
    if auth_header.lower().startswith("tma "):
        return auth_header[4:].strip()

    # 3. Query parameter: ?tgWebAppData=...
    return request.args.get("tgWebAppData", "").strip()


def require_admin(fn):
    """Decorator requiring a valid Telegram WebApp signature from an admin user."""

    @wraps(fn)
    async def wrapper(*args, **kwargs):
        init_data_raw = extract_init_data()
        bot_token = get_bot_token()
        admin_ids = get_admin_ids()

        is_valid, payload, err = validate_init_data(init_data_raw, bot_token)
        if not is_valid or not payload:
            log.warning("Admin auth failed: %s", err)
            return jsonify({"error": f"Unauthorized: {err}"}), 401

        user = payload.get("user") or {}
        user_id = user.get("id")

        if not user_id or user_id not in admin_ids:
            log.warning("Forbidden access attempt by Telegram user %s", user_id)
            return jsonify({"error": "Forbidden: admin privileges required"}), 403

        g.tma_user = user
        return await fn(*args, **kwargs)

    return wrapper


def optional_auth(fn):
    """Decorator parsing initData if present, but allowing anonymous requests."""

    @wraps(fn)
    async def wrapper(*args, **kwargs):
        init_data_raw = extract_init_data()
        if init_data_raw:
            bot_token = get_bot_token()
            is_valid, payload, _ = validate_init_data(init_data_raw, bot_token)
            if is_valid and payload:
                user = payload.get("user") or {}
                user_id = user.get("id")
                admin_ids = get_admin_ids()
                g.tma_user = user
                g.is_admin = bool(user_id and user_id in admin_ids)
            else:
                g.tma_user = None
                g.is_admin = False
        else:
            g.tma_user = None
            g.is_admin = False

        return await fn(*args, **kwargs)

    return wrapper
