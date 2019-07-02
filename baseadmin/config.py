import os
import logging

logger = logging.getLogger(__name__)

import socket

from baseadmin       import __version__
from baseadmin.tools import VariableSleep

CWD = os.getcwd()

class app(object):
  version     = __version__
  name        = os.environ.get("APP_NAME")        or os.path.basename(CWD)
  root        = os.environ.get("APP_ROOT")        or CWD
  author      = os.environ.get("APP_AUTHOR")      or "Unknown Author"
  description = os.environ.get("APP_DESCRIPTION") or "A baseAdmin app"

class client_meta(type):
  @property
  def ip(cls):
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
      except Exception as e:
        pass
      finally:
        s.close()

class client(metaclass=client_meta):
  name        = os.environ.get("CLIENT_NAME")     or socket.gethostname()
  secret      = os.environ.get("CLIENT_SECRET")   or "secret"


if client.secret == "secret": logger.warn("using default client secret")

class store(object):
  uri         = os.environ.get("MONGODB_URI") \
                or "mongodb://localhost:27017/" + app.name
  timeout     = 1000

class master(object):
  root                  = os.environ.get("MASTER_ROOT") or None
  registration_interval = VariableSleep(60, 60)
  connection_interval   = VariableSleep(60, 60)
  connection_retries    = 5

logger.debug("baseAdmin config = " + str({
  "app" : {
    "name"        : app.name,
    "root"        : app.root,
    "author"      : app.author,
    "description" : app.description
  },
  "client": {
    "name"        : client.name,
    "ip"          : client.ip
  },
  "store": {
    "uri"         : store.uri,
    "timeout"     : store.timeout
  },
  "master" : {
    "root"        : master.root,
    "intervals"    : {
      "registration" : str(master.registration_interval),
      "connection"   : str(master.connection_interval)
    }
  }
}))
