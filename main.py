"""Application ASGI Entrypoint for Hypercorn / Uvicorn"""

from app.logger import log
from app.main import create_app

app = create_app()
log.info("Initialized Loglan application: %s", app.name)
