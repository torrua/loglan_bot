"""The main module for launching web application"""

from app import create_app
from app.logger import log
from waitress import serve

app = create_app()
log.debug(app.name)


if __name__ == "__main__":
    serve(app, listen='*:8080')
