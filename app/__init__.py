from flask import Flask, render_template
from flask_bootstrap import Bootstrap

from app.api.views import blueprints as api_blueprints
from app.bot import bot_blueprint

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
    app.register_blueprint(bot_blueprint, url_prefix='/bot')
    _ = [
            app.register_blueprint(bp.get("blueprint"), url_prefix=bp.get("url_prefix"))
            for bp in api_blueprints
        ]
    app.debug = True

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.route("/", methods=["GET"])
    @app.route("/index")
    def index():
        """
        example endpoint
        """
        return render_template("index.html")

    return app
