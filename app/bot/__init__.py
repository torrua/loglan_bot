"""Telegram Bot Webhook and Management Routes"""

from __future__ import annotations

from urllib.parse import urlparse

from quart import Blueprint, abort, jsonify, request
from telebot import types
from telebot.asyncio_helper import ApiTelegramException

from app.bot.telegram import TOKEN, bot
from app.config import settings
from app.logger import log

bot_blueprint = Blueprint("bot", __name__)


def _normalize_webhook_url(raw: str) -> str:
    """Normalize and build a valid Telegram webhook URL."""
    raw = (raw or "").strip()
    if not raw:
        return ""

    if "://" in raw:
        parsed = urlparse(raw)
        host = parsed.netloc or parsed.path
        path = parsed.path if parsed.netloc else ""
    else:
        parts = raw.split("/", 1)
        host = parts[0]
        path = f"/{parts[1]}" if len(parts) > 1 and parts[1] else ""

    host = host.strip("/")
    path = path.rstrip("/")

    if path in ("/bot/webhook", f"/bot/{TOKEN}"):
        endpoint = path
    else:
        endpoint = "/bot/webhook"

    return f"https://{host}{endpoint}"


def _is_admin_authorized() -> bool:
    """Check if request contains valid admin/webhook secret token."""
    secret = request.args.get("secret") or request.headers.get("X-Admin-Secret")
    if not settings.webhook_secret:
        return True  # If no secret is configured, allow for local dev
    return secret == settings.webhook_secret


@bot_blueprint.route("/webhook", methods=["POST"])
@bot_blueprint.route(f"/{TOKEN}", methods=["POST"])
async def telegram_webhook():
    """Process incoming Telegram updates from webhook."""
    # Verify Telegram secret token header if configured
    if settings.webhook_secret:
        header_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if header_secret != settings.webhook_secret:
            log.warning("Unauthorized webhook request received (invalid secret token)")
            abort(403)

    data = await request.get_json()
    if not data:
        return "No data", 400

    try:
        update = types.Update.de_json(data)
        if update:
            await bot.process_new_updates([update])
    except Exception as exc:
        log.error("Error processing update: %s", exc, exc_info=True)

    return "OK", 200


@bot_blueprint.route("/about")
async def bot_about():
    """Get public bot status or full info if authorized."""
    if not _is_admin_authorized():
        return jsonify({"status": "active", "service": "loglan_bot"}), 200

    try:
        bot_data = await bot.get_me()
        return jsonify({k: v for k, v in bot_data.to_dict().items() if v}), 200
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@bot_blueprint.route("/set")
async def set_bot_webhook():
    """Sets Telegram webhook to point to this deployment."""
    if not _is_admin_authorized():
        abort(403)

    raw_target = (
        request.args.get("url")
        or request.args.get("host")
        or settings.webhook_host
        or request.host
    )
    webhook_url = _normalize_webhook_url(raw_target)

    if any(local in webhook_url.lower() for local in ("localhost", "127.0.0.1", "0.0.0.0")):
        log.warning(
            "Webhook target '%s' contains a local address. Telegram will reject non-public URLs.",
            webhook_url,
        )
    if ":8080" in webhook_url:
        log.warning(
            "Webhook target '%s' contains port 8080. Telegram only supports ports 443, 80, 88, 8443.",
            webhook_url,
        )

    log.info("Configuring Telegram webhook to: %s", webhook_url)

    await bot.remove_webhook()
    kwargs = {"url": webhook_url}
    if settings.webhook_secret:
        kwargs["secret_token"] = settings.webhook_secret

    try:
        await bot.set_webhook(**kwargs)
        log.info("Webhook configured successfully to: %s", webhook_url)
        return f"⚓ Webhook set to: {webhook_url}", 200
    except ApiTelegramException as exc:
        log.error("Telegram API error setting webhook to %s: %s", webhook_url, exc)
        return (
            jsonify(
                {
                    "status": "error",
                    "message": "Telegram API rejected webhook URL",
                    "attempted_url": webhook_url,
                    "telegram_error": exc.description,
                    "error_code": exc.error_code,
                    "hint": (
                        "Telegram webhooks require a public HTTPS URL with a valid SSL certificate. "
                        "Only ports 443, 80, 88, and 8443 are supported. "
                        "Addresses with localhost, 127.0.0.1, or port 8080 are rejected by Telegram."
                    ),
                }
            ),
            400,
        )


@bot_blueprint.route("/del")
async def delete_bot_webhook():
    """Deletes current Telegram webhook."""
    if not _is_admin_authorized():
        abort(403)

    await bot.remove_webhook()
    log.info("Webhook deleted")
    return "🔱 Webhook was deleted.", 200
