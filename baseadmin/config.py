import os
import logging
import socket

CWD = os.getcwd()

class app(object):
  name        = os.environ.get("APP_NAME")        or os.path.basename(CWD)
  root        = os.environ.get("APP_ROOT")        or CWD
  author      = os.environ.get("APP_AUTHOR")      or "Unknown Author"
  description = os.environ.get("APP_DESCRIPTION") or "A baseAdmin app"

class client(object):
  name        = os.environ.get("CLIENT_NAME")     or socket.gethostname()
  secret      = os.environ.get("CLIENT_SECRET")   or "secret"

if client.secret == "secret":
  logging.warn("using default client secret")

class store(object):
  uri         = os.environ.get("MONGODB_URI") \
                or "mongodb://localhost:27017/" + app.name
  timeout     = 1000

class messaging(object):
  uri         = os.environ.get("CLOUDMQTT_URL") \
                or os.environ.get("MQTT_URL"),
  cloud       = not os.environ.get("CLOUDMQTT_URL") is None

logging.debug("baseAdmin config = " + str({
  "App" : {
    "name"        : app.name,
    "root"        : app.root,
    "author"      : app.author,
    "description" : app.description
  },
  "client": {
    "name"        : client.name
  },
  "Store": {
    "uri"         : store.uri,
    "timeout"     : store.timeout
  },
  "Messaging" : {
    "uri"         : messaging.uri,
    "cloud"       : messaging.cloud
  }
}))
