import logging
import traceback

from flask         import request, Response
from flask_restful import Resource

from baseadmin                       import config
from baseadmin.backend.security      import authenticated
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
      return clients.request(
        request.authorization.username,
        request.get_json()
      )
    except Exception as e:
      return Response(str(e), 500)

api.add_resource(ClientRegistration, "/api/clients/register")

class ClientMaster(Resource):
  @authenticated("clients")
  def get(self):
    try:
      info = clients.get(request.authorization.username)
      logging.debug("providing {0}".format(info))
      return info
    except Exception as e:
      exception = traceback.format_exc()
      logging.error(exception)
      return Response(str(e), 500)

api.add_resource(ClientMaster, "/api/clients/master")
