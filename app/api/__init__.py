"""LOD Manager REST API Blueprint for Telegram Mini App and Web."""

from quart import Blueprint

api_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")

from . import routes  # noqa: E402, F401

__all__ = ["api_bp"]
