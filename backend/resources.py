import os
import logging

from urllib.parse import urlparse

from flask_restful import Resource

from backend import app, api, mongo, authenticate

class Connection(Resource):
  @authenticate(["admin"])
  def get(self):
    return {
      'status': 'OK',
      'mongo': str(mongo.db),
    }

api.add_resource(Connection, "/api/status")

class MQTT(Resource):
  @authenticate(["admin"])
  def get(self):
    uri = os.environ.get("CLOUDMQTT_URL")
    if not uri:
      logging.warn("cloudn't retrieve CLOUDMQTT_URL env variable")
      return None
    p = urlparse(uri)
    return {
      "ssl"     : p.scheme == "wss" or p.port == 19044,
      "hostname": p.hostname,
      "port"    : 39044 if p.port == 19044 else p.port,
      "username": p.username,
      "password": p.password
    }

api.add_resource(MQTT, "/api/mqtt/connection")
