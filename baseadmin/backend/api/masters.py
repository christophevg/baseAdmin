import logging

from flask         import request, Response
from flask_restful import Resource

from baseadmin                       import config
from baseadmin.backend.security      import authenticated
from baseadmin.backend.api           import api
from baseadmin.backend.repositories  import masters

class Masters(Resource):
  @authenticated("users")
  def post(self):
    try:
      master = request.get_json()["master"]
      masters.accept(master)
    except:
      logging.exception("failed to accept {0}".format(master))
      return Response("failed to accept master", 500)

api.add_resource(Masters, "/api/masters")
