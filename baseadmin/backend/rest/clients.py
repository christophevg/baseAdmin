from flask         import request
from flask_restful import Resource

from baseadmin                       import config
from baseadmin.backend.rest          import api
from baseadmin.backend.security      import authenticate
from baseadmin.backend.repositories  import clients

class ClientRegistration(Resource):
  @authenticate([config["register"]["user"]])
  def post(self):
    clients.register(request.get_json())

api.add_resource(ClientRegistration, "/api/clients/register")
