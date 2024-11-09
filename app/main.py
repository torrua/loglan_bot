from quart import Quart, render_template

from app.bot import bot_blueprint
from app.site.routes import site_blueprint


def create_app():
    """
    Create app
    """

    new_app = Quart(__name__)
    new_app.register_blueprint(bot_blueprint, url_prefix="/bot")
    new_app.register_blueprint(site_blueprint, url_prefix="/site")
    new_app.debug = False

    @new_app.errorhandler(404)
    async def page_not_found(_):
        return await render_template("404.html"), 404

    @new_app.route("/", methods=["GET"])
    @new_app.route("/index")
    async def index():
        """
        example endpoint
        """
        return await render_template("index.html")

    return new_app


if __name__ == "__main__":
    app = create_app()
    app.run()
