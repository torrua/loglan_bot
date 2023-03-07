# -*- coding: utf-8 -*-
"""The main module for launching web application"""

import os
from bot import bot, APP_SITE, TOKEN


if __name__ == "__main__":
        bot.remove_webhook()
        bot.polling()
