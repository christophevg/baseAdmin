import logging
logger = logging.getLogger(__name__)

from pymongo.errors import DuplicateKeyError

from baseadmin.storage              import db
from baseadmin.backend.socketio     import socketio
from baseadmin.backend.repositories import clients

def request(name, token):
  try:
    # if the request exists return its state/outcome
    registration = get(name)
    if registration:
      if registration["state"] == "accepted":
        client = clients[name]
        return {
          "state" : "accepted",
          "master": clients[client.master].location if client.master else None
        }
    # else accept a the new request
    else:
      db.registrations.insert_one({
        "_id" : name,
        "state": "pending",
        "token": token
      })
      logger.info("received and recorded registration request from {0} with token {1}".format(name, token))
      socketio.emit("register", name, room="browser")
  except Exception as e:
    raise ValueError("invalid request: {0}".format(str(e)))
  return None # pending

def get(name=None):
  if name: return db.registrations.find_one({"_id": name})
  return [ request for request in db.registrations.find({"state": "pending"}) ]

def delete(name):
  if not get(name):
    logger.warn("deleting unknown registration: {0}".format(name))
    # raise ValueError("unknown registration for {0}".format(name))
  logger.info("deleting registration for {0}".format(name))
  db.registrations.delete_one({"_id": name})

def accept(name, master=None):
  try:
    request = get(name)
    if not request:
      logger.warn("accepting unknown registration: {0}".format(name))
      raise ValueError("unknown registration for {0}".format(name))
    # check is master is known/master
    if master:
      if (master in clients):
        if clients[master].location is None:
          logger.error("can't register with non-master {0}".format(master))
          raise ValueError("{0} is not a master".format(master))
      else:
        logger.error("can't register with unknown master {0}".format(master))
        raise ValueError("unknown master {0}".format(master))
    # create/update client record
    clients[name].update(
      token=request["token"] if master is None else None,
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
