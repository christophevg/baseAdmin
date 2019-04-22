import logging

from flask         import request, Response
from flask_restful import Resource

from baseadmin                       import config
from baseadmin.backend.security      import authenticated
from baseadmin.backend.api           import api
from baseadmin.backend.repositories  import nodes

class Nodes(Resource):
  @authenticated("clients")
  def get(self):
    node = request.authorization.username
    try:
      return nodes.get(node)
    except:
      logging.exception("failed to retrieve node {0}".format(node))
      return Response("failed to retrieve node info", 500)

  @authenticated("users")
  def post(self):
    node   = request.authorization.username
    master = None
    try:
      master = request.get_json()["master"]
      nodes.assign(node, master)
    except:
      logging.exception("failed to assign {0} to {1}".format(node, master))
      return Response("failed to assign node to master", 500)

api.add_resource(Nodes, "/api/nodes")
