__version__ = "1.0.0"

import os
import socket
import logging

from dotenv import load_dotenv
load_dotenv()

# setup logging

logger = logging.getLogger()

formatter = logging.Formatter(
  "[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s",
  "%Y-%m-%d %H:%M:%S %z"
)

if len(logger.handlers) > 0:
  logger.handlers[0].setFormatter(formatter)
else:
  consoleHandler = logging.StreamHandler()
  consoleHandler.setFormatter(formatter)
  logger.addHandler(consoleHandler)

LOG_LEVEL = os.environ.get("LOG_LEVEL") or "DEBUG"
logger.setLevel(logging.getLevelName(LOG_LEVEL))

# create global configuration dictionary from environment variables/defaults

cwd = os.getcwd()
APP_NAME = os.environ.get("APP_NAME") or os.path.basename(cwd)

config = {
  "name"        : APP_NAME,
  "root"        : os.environ.get("APP_ROOT")        or cwd,
  "author"      : os.environ.get("APP_AUTHOR")      or "Unknown Author",
  "description" : os.environ.get("APP_DESCRIPTION") or "A baseAdmin app",
  "register"    : {
    "user"      : os.environ.get("REGISTER_USER")   or "client",
    "pass"      : os.environ.get("REGISTER_PASS")   or "client" 
  },
  "admin" : {
    "pass"      : os.environ.get("ADMIN_PASS")      or "admin"
  },
  "store" : {
    "uri"       :    os.environ.get("CLOUDMQTT_URL") \
                  or os.environ.get("MONGODB_URI") \
                  or "mongodb://localhost:27017/" + APP_NAME,
    "cloud"     : not os.environ.get("CLOUDMQTT_URL") is None,
    "timeout"   : 1000
  }
}

HOSTNAME = socket.gethostname()

logging.debug("baseAdmin config = " + str(config))
