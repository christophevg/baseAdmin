import os
import logging

from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGODB_URI")
if not MONGO_URI:
  MONGO_URI = "mongodb://localhost:27017/cloud"

logging.debug("connecting to " + MONGO_URI)
mongo = MongoClient(MONGO_URI)

database = MONGO_URI.split("/")[-1]

store = mongo[database]

import baseadmin.backend.provision
