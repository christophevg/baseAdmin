import logging
logger = logging.getLogger(__name__)

import uuid

from pymongo.errors import DuplicateKeyError

from baseadmin.storage              import db
from baseadmin.backend.socketio     import socketio
from baseadmin.backend.repositories import clients

def request(name):
  try:
    # if the request exists return it
    registration = get(name)
    if registration:
      if registration["state"] == "accepted":
        client = clients[name]
        registration["master"] = clients[client.master].location if client.master else None
        registration["token"]  = client.token
      return registration
    # else accept a the new request
    db.registrations.insert_one({
      "_id" : name,
      "state": "pending"
    })
    logger.info("received and recorded registration request")
    socketio.emit("register", name, room="browser")
  except Exception as e:
    raise ValueError("invalid request: {0}".format(str(e)))
  return None

def get(name=None):
  if name: return db.registrations.find_one({"_id": name})
  return [ request for request in db.registrations.find({"state": "pending"}) ]

def delete(name):
  logger.info("deleting registration for {0}".format(name))
  db.registrations.delete_one({"_id": name})

def accept(name, master=None):
  try:
    request = get(name)
    # create/update client record
    clients[name].update(
      token=str(uuid.uuid4()) if master is None else None,
      master=master,
      location=request["location"] if "location" in request else None
    )
    # update registration status
    db.registrations.update_one(
      { "_id" : name },
      { "$set" : { "state" : "accepted" } }
    )
    if master:
      logger.info("assigned {0} to {1}".format(name, master))
    else:
      logger.info("accepted client {0} with token  {1}".format(name, clients[name].token))
  except Exception as e:
    raise ValueError("invalid request: {0}".format(str(e)))
  return None

def reject(name):
  try:
    db.registrations.update_one(
      {"_id" : "name"},
      { "$set" : { "state" : "rejected" } }
    )
    logger.info("rejected {0}".format(name))
  except Exception as e:
    raise ValueError("invalid request: {0}".format(str(e)))
  return None
