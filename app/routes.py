# -*- coding:utf-8 -*-
"""
Providing routes for our application
"""

from os import environ
from flask import request as rq
from telebot import types

from config.postgres import app
from bot import bot

APP_SITE = environ.get('APP_SITE')
TOKEN = environ.get('TELEGRAM_BOT_TOKEN')


@app.route("/%s" % TOKEN, methods=['POST'])
def get_message():
    """
    Get all messages
    :return:
    """
    bot.process_new_updates([types.Update.de_json(rq.stream.read().decode("utf-8"))])
    return "Ok", 200


@app.route('/')
@app.route('/heartbeat')
def index():
    """
    Test functionality
    :return:
    """
    return {k: v for k, v in bot.get_me().__dict__.items() if v}, 200


@app.route('/set')
def webhook():
    """
    Set telegram webhook
    :return:
    """
    bot.remove_webhook()
    bot.set_webhook(url="https://%s/%s" % (APP_SITE, TOKEN))
    return "Webhook was set.", 200


@app.route('/delete')
def delete():
    """
    Delete telegram webhook
    :return:
    """
    bot.remove_webhook()
    return "Webhook was deleted.", 200
