import logging
from logging.handlers import RotatingFileHandler

log_name = "mysite/src/logs/app_log.log"

logging.basicConfig(
    handlers = [RotatingFileHandler(log_name, maxBytes = 20000, backupCount = 0)],
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s")

def log_error(e):
    logging.error(e, exc_info=True)


