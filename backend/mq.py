import os
import logging

import paho.mqtt.client as mqtt

from urllib.parse import urlparse

from backend      import HOSTNAME, IP
from backend.web  import server
from backend.data import store


CLOUDMQTT_URL = os.environ.get("CLOUDMQTT_URL")
if not CLOUDMQTT_URL:
  CLOUDMQTT_URL = "mqtt://localhost:1883"

MQ_URI = CLOUDMQTT_URL

p = urlparse(MQ_URI)
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

subscriptions = {}

def follow(topic, callback):
  if not topic in subscriptions:
    subscriptions[topic] = set()
  subscriptions[topic].add(callback)

def on_connect(client, clientId, flags, rc):
  logging.debug("mq: connected with result code " + str(rc))
  client.subscribe("#")
  client.publish("client/status",  clientId + ":online",  1, False)

  if not msg.topic in subscriptions: return
  for callback in subscriptions[msg.topic]:
    callback(str(msg.payload.decode("utf-8")))
def on_message(client, clientId, msg):

def track_client_status(msg):
  (client, status) = str(msg).split(":")
  with server.app_context():
    store.db.clients.update_one(
      { "_id": client },
      { "$set" : { "status" : status } },
      upsert=True
    )

def track_clients():
  logging.debug("following client/status")
  follow("client/status", track_client_status)

client = None
CLIENT_ID = HOSTNAME + "@" + IP

def connect(clientId=CLIENT_ID, mq=None):
  if mq is None: mq = MQ
  clientId = clientId + "@" + HOSTNAME + "(" + IP + ")"
  client = mqtt.Client(userdata=clientId)
  if mq["username"] and mq["password"]:
    client.username_pw_set(mq["username"], mq["password"])
  client.on_connect = on_connect
  client.on_message = on_message
  client.will_set("client/status", clientId + ":offline", 1, False)
  logging.debug("connecting to MQ " + mq["hostname"] + ":" + str(mq["port"]))
  client.connect(mq["hostname"], mq["port"])
  client.loop_start()
