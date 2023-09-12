# -*- coding:utf-8 -*-
"""
Providing routes for our application
"""

from flask import Blueprint, request as rq
from telebot import types

from app.telegram_bot.bot import bot, APP_SITE, TOKEN

bot_routes = Blueprint("route", __name__)


@bot_routes.route(f"/bot/{TOKEN}", methods=["POST"])
def get_message():
    """
    Get all messages
    :return:
    """
    bot.process_new_updates([types.Update.de_json(rq.stream.read().decode("utf-8"))])
    return "Ok", 200


@bot_routes.route("/bot/about")
@bot_routes.route("/bot/heartbeat")
def index():
    """
    Test functionality
    :return:
    """
    return {k: v for k, v in bot.get_me().__dict__.items() if v}, 200


@bot_routes.route("/bot/set")
def webhook():
    """
    Set telegram webhook
    :return:
    """
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{APP_SITE}/bot/{TOKEN}")
    return "⚓ Webhook was set.", 200


@bot_routes.route("/bot/del")
def delete():
    """
    Delete telegram webhook
    :return:
    """
    bot.remove_webhook()
    return "⚓ Webhook was deleted.", 200
