import logging

logging.basicConfig(
    # format='%(message)s',
    format="%(filename)s [LINE:%(lineno)d]"
    "\t[%(asctime)s] %(levelname)-s"
    "\t%(funcName)s() \t\t%(message)s",
    level=logging.DEBUG,
    datefmt="%y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)
