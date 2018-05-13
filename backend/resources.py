import os

from urllib.parse import urlparse

from flask_restful    import Resource, abort

from backend.store    import store
from backend.security import authenticate
from backend.rest     import api

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

api.add_resource(Connection, "/api/status")

class MQInfo(Resource):
  @authenticate(["admin"])
  def get(self, scope, arg=None):
    try:
      return {
        "connection" : self.get_connection,
        "clients"    : self.get_clients
      }[scope](arg)
    except KeyError:
      abort(404, message="MQ:{} doesn't exist".format(arg))

  def get_connection(self, arg=None):
    if arg is None or arg == "ws":
      return MQ_WS;
    return MQ

  def get_clients(self, arg=None):
    return [ c for c in store.status.distinct("_id", { "status": "online" }) ]

api.add_resource(MQInfo,
  "/api/mq/<string:scope>",
  "/api/mq/<string:scope>/<string:arg>"
)
