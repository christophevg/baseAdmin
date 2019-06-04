import logging

from flask         import request, Response
from flask_restful import Resource

from baseadmin.backend.api.rest     import api
from baseadmin.backend.repositories import users

class Provisioning(Resource):
  def post(self):
    try:
      assert users.count() == 0
      provision = request.get_json()
      users.create(provision["user"])
    except:
      logging.exception(
        "failed to provision {0}".format(request.get_data(as_text=True))
      )
      return Response("failed to provision", 500)

api.add_resource(Provisioning, "/api/provision")
