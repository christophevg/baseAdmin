import os

from flask_pymongo import PyMongo

from backend import APP_NAME
from backend.web import server

MONGO_URI = os.environ.get("MONGODB_URI")
if not MONGO_URI:
  MONGO_URI = "mongodb://localhost:27017/" + APP_NAME;

server.config['MONGO_URI'] = MONGO_URI
store = PyMongo(server)

import backend.provision
