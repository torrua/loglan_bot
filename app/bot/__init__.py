# -*- coding:utf-8 -*-
"""
Providing routes for our application
"""

from flask import Blueprint, request as rq
from telebot import types

from app.bot.telegram import bot, TOKEN

bot_blueprint = Blueprint("route", __name__, template_folder='templates')


@bot_blueprint.route(f"/{TOKEN}", methods=["POST"])
def get_message():
    """
    Get all messages
    :return:
    """
    bot.process_new_updates([types.Update.de_json(rq.stream.read().decode("utf-8"))])
    return "Ok", 200


@bot_blueprint.route("/about")
def index():
    """
    Test functionality
    :return:
    """
    return {k: v for k, v in bot.get_me().__dict__.items() if v}, 200


@bot_blueprint.route("/set")
def webhook():
    """
    Set telegram webhook
    :return:
    """
    app_site = rq.host
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{app_site}/bot/{TOKEN}")
    return "⚓ Webhook was set.", 200


@bot_blueprint.route("/del")
def delete():
    """
    Delete telegram webhook
    :return:
    """
    bot.remove_webhook()
    return "⚓ Webhook was deleted.", 200
