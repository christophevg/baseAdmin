import logging

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
      client = request.authorization.username
      return clients.request(client, request.get_json())
    except:
      logging.exception(
        "failed to store request for {0}: {1}".format(
          client, request.get_data(as_text=True)
        )
      )
      return Response("failed to store registration request", 500)

api.add_resource(ClientRegistration, "/api/clients/register")


class ClientMaster(Resource):
  @authenticated("clients")
  def get(self):
    try:
      client = request.authorization.username
      return clients.get(client)["master"]
    except:
      logging.exception("failed to retrieve client {0}".format(
        request.authorization.username
      ))
      return Response("failed to retrieve client info", 500)

  @authenticated("users")
  def post(self):
    try:
      client = request.authorization.username
      master = request.get_json()["master"]
      clients.assign(client, master)
    except:
      logging.exception("failed to assign {0} to {1}".format(client, master))
      return Response("failed to assign client to master", 500)

api.add_resource(ClientMaster, "/api/clients/master")
