"""Application Logging Configuration"""

import logging
import sys


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configures application logger with standard readable format."""
    logger = logging.getLogger("loglan_bot")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger


log = setup_logging()
