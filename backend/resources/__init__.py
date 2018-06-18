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

MQTT_URL = os.environ.get("CLOUDMQTT_URL")
if not MQTT_URL:
  MQTT_URL = os.environ.get("MQTT_URL")
  if not MQTT_URL:
    MQTT_URL = "mqtt://localhost:1883"

MQ = urlparse(MQTT_URL)

MQ_WS = {
  "ssl"      : MQ.scheme == "wss" or MQ.port == 19044,
  "hostname" : MQ.hostname,
  "port"     : 39044 if MQ.port == 19044 else 9001,
  "username" : MQ.username,
  "password" : MQ.password  
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
  def get(self):
    return MQ_WS;

api.add_resource(MQInfo,
  "/api/mq/connection"
)

if MASTER: import backend.resources.master
if CLOUD:  import backend.resources.cloud
