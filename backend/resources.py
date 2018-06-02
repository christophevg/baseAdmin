import os
import logging

import bcrypt

from urllib.parse import urlparse

from bson import ObjectId

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
    clients = {};
    for client in store.status.find({}, { "lastModified": False }):
      clients[client["_id"]] = client;
    
    for client in store.config.find():
      if not client["_id"] in clients:
        clients[client["_id"]] = {
          "_id" : client["_id"],
          "status": "offline",
        }
      clients[client["_id"]]["groups"] = client["groups"] + ["all"];
      clients[client["_id"]]["services"] = client["services"];
    
    return clients.values();

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

class Users(Resource):
  @authenticate(["admin"])
  def get(self):
    return [ { "_id" : str(u["_id"]), "name": u["name"] } for u in store.users.find({}, { "password" : False })]

api.add_resource(Users,
  "/api/users"
)

class User(Resource):
  @authenticate(["admin"])
  def post(self, id):
    user = request.get_json()
    user.pop("_id", None)
    user["_id"]      = id
    # TODO apply same field validations as in form
    user["password"] = bcrypt.hashpw(user["password"], bcrypt.gensalt())
    result = store.users.insert_one(user)
    return str(result.inserted_id)

  @authenticate(["admin"])
  def put(self, id):
    user = request.get_json()
    user.pop("_id", None)
    if "password" in user:
      if user["password"] == "":
        user.pop("password", None)
      else:
        user["password"] = bcrypt.hashpw(user["password"], bcrypt.gensalt())
    store.users.update_one(
      { "_id": id },
      { "$set" : user }
    )
    return id

  @authenticate(["admin"])
  def delete(self, id):
    result = store.users.delete_one({"_id" : id})
    if result.deleted_count == 1:
      return True
    else:
      return abort(404, message="Unknown user: {}".format(id))

api.add_resource(User,
  "/api/user/<string:id>"
)
