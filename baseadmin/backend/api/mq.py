import logging

from flask         import request, Response
from flask_restful import Resource

from baseadmin                       import config
from baseadmin.backend.security      import authenticated
from baseadmin.backend.rest          import api

class Connection(Resource):
  @authenticated("users")
  def get(self):
    return config.messaging.ws

api.add_resource(Connection, "/api/mq/connection")
