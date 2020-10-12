# -*- coding: utf-8 -*-
"""The main module for launching Heroku application"""

from os import environ
from config.postgres import app

ENV = environ["ENVIRONMENT"]

if __name__ == "__main__":
    # pylint: disable=W0106
    from bot import bot, APP_SITE, TOKEN

    if int(ENV) == 0:
        bot.remove_webhook()
        bot.polling()
    else:
        bot.set_webhook(url="https://%s/%s" % (APP_SITE, TOKEN))
        app.run(host="0.0.0.0", port=int(environ.get('PORT', 5000)))
