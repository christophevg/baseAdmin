import logging

from flask         import request, Response
from flask_restful import Resource

from baseadmin                       import config
from baseadmin.backend.api           import api
from baseadmin.backend.repositories  import registration

class Registration(Resource):
  def post(self):
    if not request.authorization or \
       not request.authorization.password == config.client.secret:
      logging.info("registration authorisation failed")
      return Response(
        "", 401, { "WWW-Authenticate": 'Basic realm="registration"' }
      )
    try:
      requestor = request.authorization.username
      return registration.request(requestor, request.get_json())
    except:
      logging.exception(
        "failed to store request for {0}: {1}".format(
          requestor, request.get_data(as_text=True)
        )
      )
      return Response("failed to handle registration request", 500)

api.add_resource(Registration, "/api/register")
