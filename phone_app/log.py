import logging
from logging.handlers import RotatingFileHandler, SysLogHandler

from const import HOST

KB = 1024
MB = 1024 * KB

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(filename)s:%(funcName)s:%(lineno)d | %(message)s"
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

fh = RotatingFileHandler(
    "/tmp/phone_app.log", maxBytes=1 * MB, encoding="utf-8", backupCount=1
)
fh.setFormatter(formatter)
logger.addHandler(fh)

if not HOST:
    sh = SysLogHandler(address="/dev/log")
    sh.setFormatter(formatter)
    logger.addHandler(sh)
