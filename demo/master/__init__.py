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

logging.getLogger("gunicorn.error").setLevel(logging.INFO)
logging.getLogger("engineio.client").setLevel(logging.WARN)
logging.getLogger("engineio.server").setLevel(logging.WARN)
logging.getLogger("socketio.client").setLevel(logging.WARN)

logging.getLogger().handlers[0].setFormatter(formatter)

from threading import Thread

from baseadmin          import config
from baseadmin.storage  import db
from baseadmin.endpoint import register, run

master = db.config.find_one({"_id": "master"})
if master: master = master["value"]

try:
  if not master:
    if not register({"location": "https://{0}:8001".format(config.client.ip)}):
      logger.fatal("registration was rejected, can't continue.")
      sys.exit(1)
  t = Thread(target=run)
  t.daemon = True
  t.start()
except KeyboardInterrupt:
  pass
