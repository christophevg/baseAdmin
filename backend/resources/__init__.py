import os
import logging

try:
  from urllib.parse import urlparse
except ImportError:
  from urlparse import urlparse

from bson import ObjectId

from flask            import request
from flask_restful    import Resource, abort

from backend.store    import store
from backend.security import authenticate
from backend.rest     import api

from backend          import MASTER, CLOUD

MQTT_URL = os.environ.get("MQTT_URL")
if not MQTT_URL:
  MQTT_URL = "mqtt://localhost:1883"

p = urlparse(MQTT_URL)
MQ = {
  "hostname" : p.hostname,
  "port"     : p.port,
  "username" : p.username,
  "password" : p.password
}

MQ_WS = {
  "ssl"      : p.scheme == "wss" or p.port == 19044,
  "hostname" : p.hostname,
  "port"     : 39044 if p.port == 19044 else 9001,
  "username" : p.username,
  "password" : p.password  
}

class Connection(Resource):
  @authenticate(["admin"])
  def get(self):
    return {
      'status': 'OK',
      'store': str(store),
    }

api.add_resource(Connection,
  "/api/status"
)

class MQInfo(Resource):
  @authenticate(["admin"])
  def get(self, arg=None):
    if arg is None or arg == "ws":
      return MQ_WS;
    return MQ

api.add_resource(MQInfo,
  "/api/mq/connection",
  "/api/mq/connection/<string:arg>"
)

if MASTER: import backend.resources.master
if CLOUD:  import backend.resources.cloud
