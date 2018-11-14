import flask_restful
from flask import make_response

from bson.json_util import dumps

from baseadmin.backend.web import server

# setup the REST-api with JSON output
def output_json(obj, code, headers=None):
  resp = make_response(dumps(obj), code)
  resp.headers.extend(headers or {})
  return resp

api = flask_restful.Api(server)
api.representations = { 'application/json': output_json }
