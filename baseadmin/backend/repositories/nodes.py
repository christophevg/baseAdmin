import logging

from pymongo.errors import DuplicateKeyError

from baseadmin.storage import db

def assign(name, master):
  request = db.requests.find_one({"_id": name})
  request["master"] = master
  db.nodes.insert_one(request)
  db.requests.delete_one({"_id": name})
  logging.info("assigned {0} to {1}".format(name, master))

def get(name):
  return db.nodes.find_one({"_id": name})
