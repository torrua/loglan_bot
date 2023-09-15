from flask import Flask, render_template
from flask_bootstrap import Bootstrap

from app.api.views import blueprints as api_blueprints
from app.telegram_bot.routes import bot_routes

bootstrap = Bootstrap()



def create_app():
    """
    Create app
    """

    # app initialization
    app = Flask(__name__)

    # bootstrap initialization
    bootstrap.init_app(app)
    # register all blueprints
    app.register_blueprint(bot_routes)
    _ = [
            app.register_blueprint(bp.get("blueprint"), url_prefix=bp.get("url_prefix"))
            for bp in api_blueprints
        ]

    @app.route("/", methods=["GET"])
    @app.route("/index")
    def index():
        """
        example endpoint
        """
        return render_template("index.html")

    return app
