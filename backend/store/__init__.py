import os
import logging

from pymongo import MongoClient

from backend import APP_NAME

MONGO_URI = os.environ.get("MONGODB_URI")
if not MONGO_URI:
  MONGO_URI = "mongodb://localhost:27017/" + APP_NAME;

logging.debug("connecting to " + MONGO_URI)
mongo = MongoClient(MONGO_URI)
store = mongo.store

import backend.provision
