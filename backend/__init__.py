import os
from functools import wraps
import logging

from flask import Flask, Response, request
import flask_restful
from flask_pymongo import PyMongo
from flask import make_response

from bson.json_util import dumps

import bcrypt

# setup logging infrastructure

formatter = logging.Formatter(
  "%(asctime)s [%(levelname)-5.5s] %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

LOGFILE = os.environ.get("LOGFILE")
if LOGFILE:
  if not os.path.exists(LOGFILE): touch(LOGFILE)
  fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName))
  fileHandler.setFormatter(logFormatter)
  logger.addHandler(fileHandler)

# silence loggers of some libs
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


APP_NAME = os.environ.get("APP_NAME")
if not APP_NAME:
  APP_NAME = "baseAdmin"

MONGO_URI = os.environ.get("MONGODB_URI")
if not MONGO_URI:
  MONGO_URI = "mongodb://localhost:27017/" + APP_NAME;

# setup the web-application
app = Flask(__name__)
app.config['MONGO_URI'] = MONGO_URI

# setup the mongo-instance and provision initial data if needed
mongo = PyMongo(app)

import backend.provision

# setup the REST-api with JSON output
def output_json(obj, code, headers=None):
  resp = make_response(dumps(obj), code)
  resp.headers.extend(headers or {})
  return resp

api = flask_restful.Api(app)
api.representations = { 'application/json': output_json }

def valid_credentials(users, auth):
  if not auth or not auth.username or not auth.password: return False
  if not auth.username in users: return False
  user = mongo.db.users.find_one({ "_id" : auth.username })
  if not user: return False
  return bcrypt.checkpw(auth.password, user["password"])

def authenticate(users):
  def decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
      if not valid_credentials(users, request.authorization):
        return Response(
          '', 401, { 'WWW-Authenticate': 'Basic realm="' + APP_NAME + '"' }
        )
      return f(*args, **kwargs)
    return wrapper
  return decorator


# import the REST API resources and the interface routing and logic
import backend.resources
import backend.interface
