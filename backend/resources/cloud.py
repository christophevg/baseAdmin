import os
import logging
import datetime
import json

from flask            import request
from flask_restful    import Resource, abort

from backend.store    import store
from backend.security import authenticate
from backend.rest     import api

import paho.mqtt.client as mqtt

MQTT_HOST = "localhost"
MQTT_PORT = 1883

mqtt_client = mqtt.Client()
# mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
mqtt_client.connect(MQTT_HOST, MQTT_PORT)

class Masters(Resource):
  @authenticate(["admin"])
  def get(self):
    return store.masters.find()

api.add_resource(Masters, "/api/masters")

class Master(Resource):
  @authenticate(["admin"])
  def post(self, master):
    data = request.get_json()
    data["last_modified"] = datetime.datetime.now().isoformat()
    store.masters.update_one({"_id": master}, {"$set": data}, upsert=True)
    mqtt_client.publish(
      "master/" + master,
      json.dumps({
        "_id": master,
        "ip": data["ip"],
        "last_modified" : data["last_modified"]
      }),
      1, False
    )

api.add_resource(Master,
  "/api/master/<string:master>"
)
