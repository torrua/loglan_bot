# -*- coding: utf-8 -*-
"""The main module for launching web application"""

import os
from app.bot.telegram import bot

if __name__ == "__main__":
        bot.remove_webhook()
        bot.send_message(os.getenv("TELEGRAM_ADMIN_ID"), f"{bot.get_me().to_dict()}")
        bot.polling()
