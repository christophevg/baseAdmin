import logging

import flask_restful
from flask import make_response

import json

from baseadmin.backend.web import server

def output_json(data, code, headers=None):
  resp = make_response(json.dumps(data), code)
  resp.headers.extend(headers or {})
  return resp

api = flask_restful.Api(server)
api.representations = { 'application/json': output_json }

import baseadmin.backend.api.provisioning
import baseadmin.backend.api.clients
import baseadmin.backend.api.mq
