import os
import logging
import pymongo

from baseadmin import config

class Database(object):
  def __init__(self):
    self.mongo    = None
    self.instance = None
  
  def connect(self):
    logging.debug("connecting to " + config.store.uri)
    if not self.mongo:
      self.mongo = pymongo.MongoClient(
        config.store.uri,
        serverSelectionTimeoutMS=config.store.timeout
      )
    database = config.store.uri.split("/")[-1]
    self.instance = self.mongo[database]
  
  def __getattr__(self, collection):
    if collection == "_pytestfixturefunction": return None
    return self[collection]

  def __getitem__(self, collection):
    if not self.instance: self.connect()
    return self.instance[collection]

  def list_collection_names(self):
    if not self.instance: self.connect()
    return self.instance.list_collection_names()

  def provision(self, collection, data):
    if not collection in self.list_collection_names():
      logging.info("provisioning " + collection)
      self.instance[collection].insert_many(data)

db = Database()
