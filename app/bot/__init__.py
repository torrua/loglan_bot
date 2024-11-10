"""
Providing routes for our application
"""

from quart import Blueprint, request as rq
from telebot import types

from app.bot.telegram import bot, TOKEN

bot_blueprint = Blueprint("route", __name__)


@bot_blueprint.route(f"/{TOKEN}", methods=["POST"])
async def get_message():
    """
    Get all messages
    :return:
    """
    await bot.process_new_updates([types.Update.de_json(await rq.get_json())])
    return "Ok", 200


@bot_blueprint.route("/about")
async def index():
    """
    Test functionality
    :return:
    """
    bot_data = await bot.get_me()
    return {k: v for k, v in bot_data.to_dict().items() if v}, 200


@bot_blueprint.route("/set")
async def webhook():
    """
    Set telegram webhook
    :return:
    """
    app_site = rq.host
    await bot.remove_webhook()
    await bot.set_webhook(url=f"https://{app_site}/bot/{TOKEN}")
    return "⚓ Webhook was set.", 200


@bot_blueprint.route("/del")
async def delete():
    """
    Delete telegram webhook
    :return:
    """
    await bot.remove_webhook()
    return "🔱 Webhook was deleted.", 200
