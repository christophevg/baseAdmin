import os
import logging

from pymongo        import MongoClient
from pymongo.errors import ConnectionFailure

class NotAvailableError(Exception):
  pass

def setup(store):
  logging.debug("connecting to " + store["uri"])
  mongo = MongoClient(store["uri"], serverSelectionTimeoutMS=store["timeout"])
  try:
    mongo.admin.command("ismaster")
    database = store["uri"].split("/")[-1]
    return mongo[database]
  except ConnectionFailure as e:
    raise NotAvailableError("{0} : {1}".format(store["uri"], str(e)))

def load(db, collection, data, force=False):
  if force or not collection in db.list_collection_names():
    logging.info("provisioning " + collection)
    if force:
      logging.info("dropping existing collection: " + collection)
      db[collection].drop();
    logging.info("provisioning collection: " + collection)
    db[collection].insert_many(data)
