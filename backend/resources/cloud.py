import os
import logging
import datetime
import json

from flask            import request
from flask_restful    import Resource, abort

import paho.mqtt.client as mqtt

from backend.store     import store
from backend.security  import authenticate
from backend.rest      import api
from backend.resources import MQ

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

api.add_resource(Master,
  "/api/master/<string:master>"
)

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

api.add_resource(Client,
  "/api/client/<string:client>"
)
