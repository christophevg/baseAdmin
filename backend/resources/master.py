import os
import logging

import bcrypt

from bson import ObjectId

from flask            import request
from flask_restful    import Resource, abort

from backend.store    import store
from backend.security import authenticate
from backend.rest     import api

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
    try:
      return store.system.find_one({"_id" : client })["stats"]
    except:
      return None

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
