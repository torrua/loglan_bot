# -*- coding: utf-8 -*-
"""The main module for launching web application"""

import os
from app import app
from bot import bot, APP_SITE, TOKEN

ENV = os.environ["ENVIRONMENT"]

if __name__ == "__main__":
    # pylint: disable=W0106

    if int(ENV) == 0:
        bot.remove_webhook()
        bot.polling()
    else:
        bot.set_webhook(url="https://%s/%s" % (APP_SITE, TOKEN))
        # heroku app.run(host="0.0.0.0", port=int(environ.get('PORT', 5000)))
        if int(ENV) == 2:
            app.run()  # railway.app
        else:
            app.run(debug=True, port=os.getenv("PORT", default=5000))  # koyeb.com
