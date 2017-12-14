import os

from flask_restful    import Resource, abort

from backend.data     import store
from backend.security import authenticate
from backend.rest     import api
from backend.mq       import MQ, MQ_WS

class Connection(Resource):
  @authenticate(["admin"])
  def get(self):
    return {
      'status': 'OK',
      'store': str(store.db),
    }

api.add_resource(Connection, "/api/status")

class MQInfo(Resource):
  @authenticate(["admin"])
  def get(self, scope, arg=None):
    try:
      return {
        "connection" : self.get_connection,
        "clients"    : self.get_clients
      }[scope](arg)
    except KeyError:
      abort(404, message="MQ:{} doesn't exist".format(arg))

  def get_connection(self, arg=None):
    if arg is None or arg == "ws":
      return MQ_WS;
    return MQ

  def get_clients(self, arg=None):
    return [ c for c in store.db.clients.distinct("_id", { "status": "online" }) ]

api.add_resource(MQInfo,
  "/api/mq/<string:scope>",
  "/api/mq/<string:scope>/<string:arg>"
)
