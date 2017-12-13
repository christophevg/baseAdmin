import os

from flask_restful    import Resource, abort

from backend.data     import store
from backend.security import authenticate
from backend.rest     import api
from backend.mq       import MQ_SSL, MQ_HOSTNAME, MQ_PORT, MQ_USERNAME, MQ_PASSWORD

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
        "connection" : self.get_connection
      }[arg]()
    except KeyError:
      abort(404, message="MQ:{} doesn't exist".format(arg))

  def get_connection(self):
    return {
      "ssl"     : MQ_SSL,
      "hostname": MQ_HOSTNAME,
      "port"    : MQ_PORT,
      "username": MQ_USERNAME,
      "password": MQ_PASSWORD
    }

api.add_resource(MQ, "/api/mq/<string:arg>")
