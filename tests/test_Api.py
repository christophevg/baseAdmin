import mongomock

import json

from base64 import b64encode

from flask_restful import Resource

from baseadmin.backend import init
init(mongomock.MongoClient().db)
from baseadmin.backend import db

from baseadmin              import pki

from baseadmin.backend.web  import server
from baseadmin.backend.rest import api, sign, signed


class TestSignature(Resource):
  @signed
  def post(self):
    return True

api.add_resource(TestSignature, "/api/test/signature")

def test_validation_of_correct_signature():
  key, public = pki.generate_key_pair()
  db.pki.drop()
  db.pki.insert_one({
    "_id": "testing",
    "public": pki.encode(public)
  })
  payload = { "test" : "ok" }
  message = sign(payload, key, origin="testing")
  
  response = server.test_client().post("/api/test/signature", 
                                       data=json.dumps(message),
                                       content_type='application/json')

test_validation_of_correct_signature()

def test_failing_validation_of_incorrect_signature():
  key, public = pki.generate_key_pair()
  db.pki.drop()
  db.pki.insert_one({
    "_id": "testing",
    "public": pki.encode(public)
  })
  payload = { "test" : "ok" }

  encoded   = b64encode(json.dumps(payload))
  signature = b64encode(pki.sign(encoded, key))
  message = {
    "payload" : payload,
    "security" : {
      "origin"    : "testing2",   # <<<<<<<<<<< !!!!!!!
      "encoded"   : encoded,
      "signature" : signature
    }
  }

  response = server.test_client().post("/api/test/signature",
                                       data=json.dumps(message),
                                       content_type='application/json')

