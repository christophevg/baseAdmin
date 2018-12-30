import logging

from functools import wraps

import flask_restful
from flask import make_response, request, abort

import json

from base64 import b64encode, b64decode

from baseadmin               import pki

from baseadmin.backend       import db, private_key
from baseadmin.backend.web   import server

def sign(payload, key=private_key, origin=""):
  encoded   = b64encode(json.dumps(payload))
  signature = b64encode(pki.sign(encoded, key))
  return {
    "payload" : payload,
    "security" : {
      "origin"    : origin,
      "encoded"   : encoded,
      "signature" : signature
    }
  }

def has_valid_signature(message):
  try:
    key = pki.decode(db.pki.find_one({"_id": message["security"]["origin"]})["public"])
    pki.validate(message["security"]["encoded"], message["security"]["signature"], key)
    payload = json.loads(b64decode(message["security"]["encoded"]))
    assert payload == message["payload"]
    return True
  except Exception as e:
    logging.error(e)
    return False

def signed(f):
  @wraps(f)
  def wrapper(self):
    if not has_valid_signature(request.get_json()):
      return abort("invalid signature")
    return f(self)
  return wrapper

def output_json(data, code, headers=None):
  resp = make_response(json.dumps(sign(data)), code)
  resp.headers.extend(headers or {})
  return resp

api = flask_restful.Api(server)
api.representations = { 'application/json': output_json }

import baseadmin.backend.rest.clients
