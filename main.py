# -*- coding: utf-8 -*-
"""The main module for launching Heroku application"""

from os import environ

from app import app
from bot import bot, APP_SITE, TOKEN

ENV = environ["ENVIRONMENT"]


if __name__ == "__main__":
    # pylint: disable=W0106

    if int(ENV) == 1:
        bot.remove_webhook()
        bot.polling()
    else:
        bot.set_webhook(url="https://%s/%s" % (APP_SITE, TOKEN))
        app.run(host="0.0.0.0", port=int(environ.get('PORT', 5000)))
