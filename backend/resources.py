import os

from flask_restful    import Resource, abort

from backend.data     import store
from backend.security import authenticate
from backend.rest     import api
from backend.mq       import MQ_WS_SSL, MQ_WS_HOSTNAME, MQ_WS_PORT, MQ_WS_USERNAME, MQ_WS_PASSWORD

class Connection(Resource):
  @authenticate(["admin"])
  def get(self):
    return {
      'status': 'OK',
      'store': str(store.db),
    }

api.add_resource(Connection, "/api/status")

class MQ(Resource):
  @authenticate(["admin"])
  def get(self, arg):
    try:
      return {
        "connection" : self.get_connection,
        "clients"    : self.get_clients
      }[arg]()
    except KeyError:
      abort(404, message="MQ:{} doesn't exist".format(arg))

  def get_connection(self):
    return {
      "ssl"     : MQ_WS_SSL,
      "hostname": MQ_WS_HOSTNAME,
      "port"    : MQ_WS_PORT,
      "username": MQ_WS_USERNAME,
      "password": MQ_WS_PASSWORD
    }

  def get_clients(self):
    return [ c for c in store.db.clients.distinct("_id", { "status": "online" }) ]

api.add_resource(MQ, "/api/mq/<string:arg>")
