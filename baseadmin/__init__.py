__version__ = "1.0.0"

import os
import socket
import logging

from dotenv import load_dotenv
load_dotenv()

from baseadmin import store, pki

class Error(Exception): pass

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
    "uri"       : os.environ.get("MONGODB_URI") \
                  or "mongodb://localhost:27017/" + APP_NAME,
    "timeout"   : 1000
  },
  "messaging" : {
    "uri"       :    os.environ.get("CLOUDMQTT_URL") \
                  or os.environ.get("MQTT_URL"),
    "cloud"     : not os.environ.get("CLOUDMQTT_URL") is None
  }
}

HOSTNAME = socket.gethostname()

logging.debug("baseAdmin config = " + str(config))

db          = None
private_key = None
public_key  = None

def init(provided_db=None):
  global db, private_key, public_key
  try:
    db = provided_db or store.setup(config["store"])
    provision_pki(db)
    keys = db.pki.find_one({"_id": ""})
    private_key = pki.decode(str(keys["key"]))
    public_key  = pki.decode(str(keys["public"]))
  except store.NotAvailableError as e:
    raise Error("could not initialize store: {0}".format(str(e)))
  logging.debug("baseAdmin is initialized...")

def get_db():
  global db
  if db is None: init()
  return db

def provision_pki(db, force=False):
  key, public = pki.generate_key_pair()
  store.load(
    db,
    "pki",
    [
      {
        "_id"    : "",
        "key"    : pki.encode(key),
        "public" : pki.encode(public)
      }
    ],
    force
  )
