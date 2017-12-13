import os
import logging

from urllib.parse import urlparse

from flask_restful import Resource

from backend.data import store
from backend.security import authenticate
from backend.rest import api

class Connection(Resource):
  @authenticate(["admin"])
  def get(self):
    return {
      'status': 'OK',
      'store': str(store.db),
    }

api.add_resource(Connection, "/api/status")

CLOUDMQTT_URL = os.environ.get("CLOUDMQTT_URL")
if not CLOUDMQTT_URL:
  CLOUDMQTT_URL = "ws://localhost:9001"

MQTT_URI = CLOUDMQTT_URL
p = urlparse(MQTT_URI)
MQTT_SSL      = p.scheme == "wss" or p.port == 19044
MQTT_HOSTNAME = p.hostname
MQTT_PORT     = 39044 if p.port == 19044 else p.port
MQTT_USERNAME = p.username
MQTT_PASSWORD = p.password

class MQTT(Resource):
  @authenticate(["admin"])
  def get(self):
    return {
      "ssl"     : MQTT_SSL,
      "hostname": MQTT_HOSTNAME,
      "port"    : MQTT_PORT,
      "username": MQTT_USERNAME,
      "password": MQTT_PASSWORD
    }

api.add_resource(MQTT, "/api/mqtt/connection")
