import logging

from pymongo.errors import DuplicateKeyError

from baseadmin.storage import db

def request(name, request):
  master = db.masters.find_one({"_id" : name})
  if master: return master

  if not db.requests.find_one({"_id" : name}):
    try:
      db.requests.insert_one({
        "_id"     : name,
        "pass"    : request["pass"],
        "pubkey"  : request["pubkey"],
        "location": request["location"],
        "role"    : "master"
      })
      logging.info("received master registration request for {0}".format(name))
    except DuplicateKeyError:
      pass
    except KeyError as e:
      raise ValueError("invalid request: {0}".format(str(e)))
  return None

def accept(name):
  request = db.requests.find_one({"_id": name})
  db.masters.insert_one(request)
  db.requests.delete_one({"_id": name})
  logging.info("accepted master {0}".format(name))

def get(name):
  return db.masters.find_one({"_id": name})
