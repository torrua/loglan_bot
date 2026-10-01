"""Quart Application Factory and Entrypoint"""

from __future__ import annotations

import os

from quart import Quart, render_template
from quart_cors import cors

from app.api import api_bp
from app.bot import bot_blueprint
from app.config import settings
from app.logger import log
from app.site.routes import site_blueprint


def create_app() -> Quart:
    """Creates and configures the Quart ASGI application instance."""
    app = Quart(__name__, template_folder="templates")

    # Configure CORS origins from environment with safe public defaults
    allowed_origins = [
        "https://torrua.github.io",
        "http://localhost:5173",
        "http://localhost:4173",
    ]
    cors_env = os.getenv("CORS_ORIGINS", "").strip()
    if cors_env:
        for origin in cors_env.split(","):
            cleaned = origin.strip()
            if cleaned and cleaned not in allowed_origins:
                allowed_origins.append(cleaned)

    app = cors(
        app,
        allow_origin=allowed_origins,
        allow_headers=["Content-Type", "Authorization", "X-Telegram-Init-Data"],
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )
    app.config["DEBUG"] = settings.debug

    # Register blueprints
    app.register_blueprint(bot_blueprint, url_prefix="/bot")
    app.register_blueprint(site_blueprint, url_prefix="/site")
    app.register_blueprint(api_bp)

    @app.errorhandler(404)
    async def page_not_found(_):
        return await render_template("404.html"), 404

    @app.errorhandler(500)
    async def server_error(error):
        log.error("Internal server error: %s", error)
        return "Internal Server Error", 500

    @app.route("/", methods=["GET"])
    @app.route("/index")
    async def index():
        """Root landing page."""
        return await render_template("index.html")

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host=settings.host, port=settings.port)
