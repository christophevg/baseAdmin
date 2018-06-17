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
