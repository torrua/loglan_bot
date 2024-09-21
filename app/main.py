from flask import Flask, render_template

from flask_bootstrap import Bootstrap

from app.bot import bot_blueprint
from app.site import site_blueprint

bootstrap = Bootstrap()


def create_app():
    """
    Create app
    """

    new_app = Flask(__name__)
    bootstrap.init_app(new_app)
    new_app.register_blueprint(bot_blueprint, url_prefix="/bot")
    new_app.register_blueprint(site_blueprint, url_prefix="/site")
    new_app.debug = True

    @new_app.errorhandler(404)
    def page_not_found(_):
        return render_template("404.html"), 404

    @new_app.route("/", methods=["GET"])
    @new_app.route("/index")
    def index():
        """
        example endpoint
        """
        return render_template("index.html")

    return new_app


app = create_app()

if __name__ == "__main__":
    app.run()
