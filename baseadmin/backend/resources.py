import os
import logging
import socket
import datetime
import json

try:
  from urllib.parse import urlparse
except ImportError:
  from urlparse import urlparse

import bcrypt

from bson import ObjectId

from flask            import request
from flask_restful    import Resource, abort

import paho.mqtt.client as mqtt

from baseadmin import config

from baseadmin.backend.store    import store
from baseadmin.backend.security import authenticate
from baseadmin.backend.rest     import api

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

api.add_resource(Connection, "/api/status")

class MQInfo(Resource):
  @authenticate(["admin"])
  def get(self):
    config = MQ_WS
    if config["hostname"] == "localhost":
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      try:
        s.connect(("8.8.8.8", 80))
        config["hostname"] = s.getsockname()[0]
      except Exception as e:
        return None
      finally:
        s.close()
    return config

api.add_resource(MQInfo, "/api/mq/connection")

mqtt_client = mqtt.Client()
if MQ.username and MQ.password:
  mqtt_client.username_pw_set(MQ.username, MQ.password)
mqtt_client.connect(MQ.hostname, MQ.port)
def on_connect(client, clientId, flags, rc):
  logging.debug("connected to MQTT with result code " + str(rc))
mqtt_client.on_connect = on_connect
mqtt_client.loop_start()


class Masters(Resource):
  @authenticate(["admin"])
  def get(self):
    masters = []
    for master in store.masters.find():
      master["clients"] = []
      for client in store.clients.find({"master": master["_id"]}):
        master["clients"].append(client["_id"])
      masters.append(master)
    return masters

api.add_resource(Masters, "/api/masters")

class Master(Resource):
  @authenticate(["admin"])
  def post(self, master):
    data = request.get_json()
    data["last_modified"] = datetime.datetime.now().isoformat()
    store.masters.update_one({"_id": master}, {"$set": data}, upsert=True)
    logging.debug("updated master: " + master)
    mqtt_client.publish(
      "master/" + master,
      json.dumps({
        "_id": master,
        "ip": data["ip"],
        "last_modified" : data["last_modified"]
      }),
      1, False
    )
  def delete(self, master):
    store.masters.delete_one({"_id" : master})
    store.clients.update({ "master" : master }, { "master": ""})

api.add_resource(Master, "/api/master/<string:master>")

class Client(Resource):
  @authenticate(["admin"])
  def get(self, client):
    client = store.clients.find_one({"_id": client})
    if client:
      master = store.masters.find_one({"_id": client["master"]})
      if master:
        client["master"] = master
    return client
  
  def post(self, client):
    data = request.get_json()
    store.clients.update_one({"_id": client}, {"$set" : data}, upsert=True)
    logging.debug("client " + client + " is linked to " + data["master"])

api.add_resource(Client, "/api/client/<string:client>")

class Clients(Resource):
  @authenticate(["admin"])
  def get(self):
    clients = {};
    # take all clients we have seen ... status=on/offline
    for client in store.status.find({}, { "lastModified": False }):
      clients[client["_id"]] = {
        "_id"     : client["_id"],
        "status"  : client["status"],
        "groups"  : [ "all" ],
        "services": []
      }

    # take all clients we have config information for add them if no status
    for client in store.config.find():
      if not client["_id"] in clients:
        clients[client["_id"]] = {
          "_id"     : client["_id"],
          "status"  : "offline",
          "groups"  : client["groups"] + [ "all" ],
          "services": client["services"]
        }
      else:
        clients[client["_id"]]["groups"]   += client["groups"]
        clients[client["_id"]]["services"] = client["services"]
    
    return clients.values();

api.add_resource(Clients, "/api/clients")

class Config(Resource):
  @authenticate(["admin"])
  def get(self, client, topic=None):
    config = store.config.find_one({"_id" : client })
    if config is None:
      return abort(404, message="Unknown client: {}".format(client))
    config["groups"] += ["all"]
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

api.add_resource(Stats, "/api/client/<string:client>/stats")
    
class Errors(Resource):
  @authenticate(["admin"])
  def get(self, client):
    limit = int(request.values["limit"]) if "limit" in request.values else 10
    return [ c for c in store.errors.find({
      "client" : client
    }, {"_id": False, "client": False }).sort([("ts", -1)]).limit(limit) ]

api.add_resource(Errors, "/api/client/<string:client>/errors")

class Users(Resource):
  @authenticate(["admin"])
  def get(self):
    return [ { "_id" : str(u["_id"]), "name": u["name"] } for u in store.users.find({}, { "password" : False })]

api.add_resource(Users, "/api/users")

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

api.add_resource(User, "/api/user/<string:id>")
