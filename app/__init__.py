from flask import Flask
from app.telegram_bot.routes import bot_routes

app = Flask(__name__)
app.register_blueprint(bot_routes)