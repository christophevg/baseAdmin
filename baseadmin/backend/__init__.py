__version__ = "1.0.0"

import os
import socket
import logging

cwd = os.getcwd()

config = {
  "name"        : os.environ.get("APP_NAME")        or os.path.basename(cwd),
  "root"        : os.environ.get("APP_ROOT")        or cwd,
  "author"      : os.environ.get("APP_AUTHOR")      or "Unknown Author",
  "description" : os.environ.get("APP_DESCRIPTION") or "A baseAdmin app"
}

HOSTNAME = socket.gethostname()  

logger = logging.getLogger()

formatter = logging.Formatter(
  '%(asctime)s - %(name)-10.10s - [%(levelname)-5.5s] - %(message)s'
)

if len(logger.handlers) > 0:
  logger.handlers[0].setFormatter(formatter)
else:
  consoleHandler = logging.StreamHandler()
  consoleHandler.setFormatter(formatter)
  logger.addHandler(consoleHandler)

LOG_LEVEL = os.environ.get("LOG_LEVEL") or "DEBUG"
logger.setLevel(logging.getLevelName(LOG_LEVEL))

logging.info("baseAdmin backend starting...")
