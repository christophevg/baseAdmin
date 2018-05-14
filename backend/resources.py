import os
import logging

from urllib.parse import urlparse

from flask            import request
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

class Clients(Resource):
  @authenticate(["admin"])
  def get(self):
    return [ c for c in store.status.distinct("_id", { "status": "online" }) ]

api.add_resource(Clients, "/api/clients")

class Config(Resource):
  @authenticate(["admin"])
  def get(self, client, topic=None):
    config = store.config.find_one({"_id" : client })
    if config is None:
      return abort(404, message="Unknown client: {}".format(client))
    config.pop("_id", None)
    if topic is None:
      return config
    else:
      if topic == "version":
        return config["last-message"]
      else:
        abort(404, message="Unknown config argument: {}".format(topic))

api.add_resource(Config,
  "/api/client/<string:client>",
  "/api/client/<string:client>/<string:topic>"
)

class Stats(Resource):
  @authenticate(["admin"])
  def get(self, client):
    return store.system.find_one({"_id" : client })["stats"]

api.add_resource(Stats,
  "/api/client/<string:client>/stats"
)
    
class Errors(Resource):
  @authenticate(["admin"])
  def get(self, client):
    limit = int(request.values["limit"]) if "limit" in request.values else 10
    return [ c for c in store.errors.find({
      "client" : client
    }, {"_id": False, "client": False }).sort([("ts", -1)]).limit(limit) ]

api.add_resource(Errors,
  "/api/client/<string:client>/errors"
)
