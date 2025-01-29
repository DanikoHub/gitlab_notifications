import json
import logging
from logging.handlers import RotatingFileHandler

with open('./mysite/secret_var.json', 'r') as file:
	secret_var = json.load(file)

log_name = secret_var["directory_path"] + "src/logs/" + 'app_log.log'

logging.basicConfig(
    handlers = [RotatingFileHandler(log_name, maxBytes = 20000, backupCount = 1)],
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s")

def send_e(e):
    logging.error(e, exc_info=True)


