import os
import logging

import paho.mqtt.client as mqtt

from urllib.parse import urlparse

from backend.web  import server
from backend.data import store


CLOUDMQTT_URL = os.environ.get("CLOUDMQTT_URL")
if not CLOUDMQTT_URL:
  CLOUDMQTT_URL = "mqtt://localhost:1883"

MQ_URI = CLOUDMQTT_URL

p = urlparse(MQ_URI)
MQ_SSL      = p.scheme
MQ_HOSTNAME = p.hostname
MQ_PORT     = p.port
MQ_USERNAME = p.username
MQ_PASSWORD = p.password

MQ_WS_SSL      = p.scheme == "wss" or p.port == 19044
MQ_WS_HOSTNAME = p.hostname
MQ_WS_PORT     = 39044 if p.port == 19044 else 9001
MQ_WS_USERNAME = p.username
MQ_WS_PASSWORD = p.password

subscriptions = {}

def follow(topic, callback):
  if not topic in subscriptions:
    subscriptions[topic] = set()
  subscriptions[topic].add(callback)

def on_connect(client, userdata, flags, rc):
  logging.debug("mq: connected with result code " + str(rc))
  client.subscribe("#")

def on_message(client, userdata, msg):
  if not msg.topic in subscriptions: return
  for callback in subscriptions[msg.topic]:
    callback(str(msg.payload.decode("utf-8")))

mq = mqtt.Client()
mq.on_connect = on_connect
mq.on_message = on_message

logging.debug("connecting to MQ " + MQ_HOSTNAME + ":" + str(MQ_PORT))
mq.connect(MQ_HOSTNAME, MQ_PORT)
mq.loop_start()

def track_client_status(msg):
  # clientId:[online|offline]
  (client, status) = str(msg).split(":")
  with server.app_context():
    print(client, status)
    store.db.clients.update_one(
      { "_id": client },
      { "$set" : { "status" : status } },
      upsert=True
    )

logging.debug("following client/status")
follow("client/status", track_client_status)
