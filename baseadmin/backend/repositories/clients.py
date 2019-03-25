import logging

from pymongo.errors import DuplicateKeyError

from baseadmin.storage import db

def request(name, request):
  client = db.clients.find_one({"_id" : name})
  if client: return client

  if not db.requests.find_one({"_id" : name}):
    logging.info("registering {0}".format(name))
    try:
      db.requests.insert_one({
        "_id"   : name,
        "pass"  : request["pass"],
        "pubkey": request["pubkey"]
      })
    except DuplicateKeyError:
      pass
    except KeyError as e:
      raise ValueError("invalid request: {0}".format(str(e)))
  return None

def assign(name, master):
  request = db.requests.find_one({"_id": name})
  # TODO

def get(name):
  return db.clients.find_one({"_id": name})
