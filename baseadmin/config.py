import os
import logging

logger = logging.getLogger(__name__)

import socket

try:
  from urllib.parse import urlparse
except ImportError:
  from urlparse import urlparse

from baseadmin       import __version__
from baseadmin.tools import VariableSleep

CWD = os.getcwd()

class app(object):
  version     = __version__
  name        = os.environ.get("APP_NAME")        or os.path.basename(CWD)
  root        = os.environ.get("APP_ROOT")        or CWD
  author      = os.environ.get("APP_AUTHOR")      or "Unknown Author"
  description = os.environ.get("APP_DESCRIPTION") or "A baseAdmin app"

class client(object):
  name        = os.environ.get("CLIENT_NAME")     or socket.gethostname()
  ip          = None
  secret      = os.environ.get("CLIENT_SECRET")   or "secret"

if client.ip is None:
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  try:
    s.connect(("8.8.8.8", 80))
    client.ip = s.getsockname()[0]
  except Exception as e:
    pass
  finally:
    s.close()

if client.secret == "secret":
  logger.warn("using default client secret")

class store(object):
  uri         = os.environ.get("MONGODB_URI") \
                or "mongodb://localhost:27017/" + app.name
  timeout     = 1000

class messaging(object):
  uri         = os.environ.get("CLOUDMQTT_URL") \
                or os.environ.get("MQTT_URL") \
                or "mqtt://localhost:1883"
  ws          = None
  cloud       = not os.environ.get("CLOUDMQTT_URL") is None

mq = urlparse(messaging.uri)

messaging.ws = {
  "ssl"      : mq.scheme == "wss" or messaging.cloud,
  "hostname" : mq.hostname,
  "port"     : 30000 + int(str(mq.port)[-4:]) if messaging.cloud else 9001,
  "username" : mq.username,
  "password" : mq.password
}

if mq.hostname == "localhost":
  messaging.ws["hostname"] = client.ip

class master(object):
  root        = os.environ.get("MASTER_ROOT") or "http://localhost:8000"
  interval    = VariableSleep(60, 60)

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
  "messaging" : {
    "uri"         : messaging.uri,
    "ws"          : messaging.ws,
    "cloud"       : messaging.cloud
  },
  "master" : {
    "root"        : master.root,
    "interval"    : str(master.interval)
  }
}))
