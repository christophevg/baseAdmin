import os

# first load the environment variables for this setup
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

LOG_LEVEL = os.environ.get("LOG_LEVEL") or "DEBUG"

# setup logging infrastructure

import logging

logging.getLogger("urllib3").setLevel(logging.WARN)

logger = logging.getLogger(__name__)

FORMAT  = "[%(asctime)s] [%(name)s] [%(process)d] [%(levelname)s] %(message)s"
DATEFMT = "%Y-%m-%d %H:%M:%S %z"

logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt=DATEFMT)
formatter = logging.Formatter(FORMAT, DATEFMT)

# import the standard baseAdmin server instance for gunicorn to consume
from baseadmin.backend.web import server

# adjust gunicorn logger to global level and formatting 
gunicorn_logger = logging.getLogger("gunicorn.error")
gunicorn_logger.handlers[0].setFormatter(formatter)
gunicorn_logger.setLevel(logging.getLevelName(LOG_LEVEL))


# connect to the baseAdmin network with an endpoint with a Master role
from baseadmin.client.endpoint import Master

from threading import Thread

try:
  endpoint = Master()
  t = Thread(target=endpoint.connect)
  t.daemon = True
  t.start()
except KeyboardInterrupt:
  pass
