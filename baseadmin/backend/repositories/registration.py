import logging
logger = logging.getLogger(__name__)

import uuid

from pymongo.errors import DuplicateKeyError

from baseadmin.storage              import db
from baseadmin.backend.socketio     import socketio
from baseadmin.backend.repositories import clients

def request(name, request):
  try:
    # if the request exists return it
    requested = get(name)
    if requested: return requested
    # else accept a the new request
    request["_id"] = name
    request["state"] = "pending"
    db.registrations.insert_one(request)
    logger.info("received and recorded registration request".format(request))
    socketio.emit("register", request, room="browser")
  except Exception as e:
    raise ValueError("invalid request: {0}".format(str(e)))
  return None

def get(name=None):
  if name: return db.registrations.find_one({"_id": name})
  return [ request for request in db.registrations.find({"state": "pending"}) ]

def delete(name):
  db.registrations.delete_one({"_id": name})

def accept(name, master=None):
  try:
    request = get(name)
    if master: master = clients[master].location
    # create/update client record
    clients[name].update(
      token=str(uuid.uuid4()) if master is None else None,
      master=master,
      location=request["location"] if "location" in request else None
    )
    # update registration with same newly assigned information (token+master)
    db.registrations.update_one(
      {"_id" : name},
      {
         "$set" : {
           "state" : "accepted",
           "token" : clients[name].token,
           "master": master
         }
      }
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
