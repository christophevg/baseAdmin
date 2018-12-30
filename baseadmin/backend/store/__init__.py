import os
import logging

from pymongo        import MongoClient
from pymongo.errors import ConnectionFailure

from baseadmin      import config

database = config["store"]["uri"].split("/")[-1]

class StoreNotAvailableError(Exception):
  pass

def setup():
  logging.debug("connecting to " + config["store"]["uri"])
  mongo = MongoClient(
    config["store"]["uri"],
    serverSelectionTimeoutMS=config["store"]["timeout"]
  )
  try:
    mongo.admin.command("ismaster")
    return mongo[database]
  except ConnectionFailure:
    raise StoreNotAvailableError(config["store"]["uri"])
