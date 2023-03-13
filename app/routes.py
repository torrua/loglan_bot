# -*- coding:utf-8 -*-
"""
Providing routes for our application
"""

from flask import request as rq
from telebot import types
from flask import Blueprint

from bot import bot, APP_SITE, TOKEN

app_routes = Blueprint("route", __name__)

@app_routes.route("/%s" % TOKEN, methods=['POST'])
def get_message():
    """
    Get all messages
    :return:
    """
    bot.process_new_updates([types.Update.de_json(rq.stream.read().decode("utf-8"))])
    return "Ok", 200


@app_routes.route('/')
@app_routes.route('/heartbeat')
def index():
    """
    Test functionality
    :return:
    """
    return {k: v for k, v in bot.get_me().__dict__.items() if v}, 200


@app_routes.route('/set')
def webhook():
    """
    Set telegram webhook
    :return:
    """
    bot.remove_webhook()
    bot.set_webhook(url="https://%s/%s" % (APP_SITE, TOKEN))
    return "⚓ Webhook was set.", 200


@app_routes.route('/delete')
def delete():
    """
    Delete telegram webhook
    :return:
    """
    bot.remove_webhook()
    return "⚓ Webhook was deleted.", 200
