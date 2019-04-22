import logging

from pymongo.errors import DuplicateKeyError

from baseadmin.storage import db

from baseadmin.repositories import nodes, masters

def request(name, request):
  try:
    existing = {
      "node"  : nodes.get,
      "master": master.get
    }[request["role"]](name)
    if existing: return existing

    try:
      request["_id"] = name
      db.requests.insert_one(request)
      logging.info("received registration request for {0}".format(name))
    except DuplicateKeyError:
      pass
  except:
    raise ValueError("invalid request: {0}".format(str(e)))
  return None
