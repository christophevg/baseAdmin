import os

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

class Environment(Resource):
  @authenticate(["admin"])
  def get(self, variable):
    return os.environ.get(variable)

api.add_resource(Environment, "/api/env/<string:variable>")
