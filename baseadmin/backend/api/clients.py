import logging

from flask         import request, Response
from flask_restful import Resource

from baseadmin                       import config
from baseadmin.backend.rest          import api
from baseadmin.backend.repositories  import clients

class ClientRegistration(Resource):
  def post(self):
    if not request.authorization or \
       not request.authorization.password == config.client.secret:
      logging.info("registration authorisation failed")
      return Response(
        "", 401, { "WWW-Authenticate": 'Basic realm="registration"' }
      )
    try:
      clients.register(request.get_json())
    except Exception as e:
      return Response(str(e), 500)
    return Response("", 200)

api.add_resource(ClientRegistration, "/api/clients/register")
