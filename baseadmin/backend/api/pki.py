from flask_restful import Resource

import simple_rsa as rsa

from baseadmin.pki         import keys
from baseadmin.backend.api import api

class PublicKey(Resource):
  def get(self):
    return rsa.encode(keys.public)

api.add_resource(PublicKey, "/api/pki/pub")
