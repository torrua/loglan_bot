"""
Главный модуль запуска приложения на Heroku и вообще
"""
from os import environ

from bot import app, bot, APP_SITE, TOKEN

# how to undo last git commit
#   git log --oneline
#   git reset HEAD@{1}

ENV = environ["ENVIRONMENT"]


if __name__ == "__main__":
    # pylint: disable=W0106

    if int(ENV) == 1:
        bot.remove_webhook()
        bot.polling()
    else:
        bot.set_webhook(url="https://%s/%s" % (APP_SITE, TOKEN))
        app.run(host="0.0.0.0", port=int(environ.get('PORT', 5000)))
