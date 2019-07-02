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

from baseadmin          import config, endpoint
from baseadmin.storage  import db

endpoint.publish_location = True

from baseadmin import config

# import custom components
from baseadmin.components.monitoring       import ping
from baseadmin.components.system.actions   import master
from baseadmin.components.system.screen    import master
from baseadmin.components.system.wifi      import master
from baseadmin.components.content          import upload
from baseadmin.components.content.download import master

# run endpoint event_loop in thread
t = Thread(target=endpoint.run)
t.daemon = True
t.start()
