import os
import logging
import pymongo

from baseadmin import config

db = None

def init():
  global db
  if not db:
    logging.debug("connecting to " + config.store.uri)
    mongo = pymongo.MongoClient(config.store.uri, serverSelectionTimeoutMS=config.store.timeout)
    database = config.store.uri.split("/")[-1]
    db = mongo[database]

def provision(collection, data):
  if not collection in db.list_collection_names():
    logging.info("provisioning " + collection)
    db[collection].insert_many(data)
