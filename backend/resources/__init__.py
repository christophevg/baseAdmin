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

MQTT_URL  = os.environ.get("CLOUDMQTT_URL")
CLOUDMQTT = not MQTT_URL is None
if not CLOUDMQTT:
  MQTT_URL = os.environ.get("MQTT_URL") or "mqtt://localhost:1883"

MQ = urlparse(MQTT_URL)

MQ_WS = {
  "ssl"      : MQ.scheme == "wss" or CLOUDMQTT,
  "hostname" : MQ.hostname,
  "port"     : 30000 + int(str(MQ.port)[-4:]) if CLOUDMQTT else 9001,
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
