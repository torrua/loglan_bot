# -*- coding: utf-8 -*-
"""The main module for launching Heroku application"""

import os
from app import app
from bot import bot, APP_SITE, TOKEN
from config import log

# Check ENV in logs
ENV = os.environ["ENVIRONMENT"]
log.debug(f"ENVIRONMENT = {ENV}")

if __name__ == "__main__":
    # pylint: disable=W0106

    if int(ENV) == 0:
        bot.remove_webhook()
        bot.polling()
    else:
        bot.set_webhook(url="https://%s/%s" % (APP_SITE, TOKEN))
        # app.run(host="0.0.0.0", port=int(environ.get('PORT', 5000)))
        app.run(debug=True, port=os.getenv("PORT", default=5000))
