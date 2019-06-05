import logging
logger = logging.getLogger(__name__)

from threading import RLock

from baseadmin.storage import db

from baseadmin.queue import MongoQueue

class Clients(object):
  def __init__(self, collection):
    self.collection = collection
    self.clients = {}
    # load all clients
    for client in self.collection.find():
      self.clients[client["_id"]] = Client(client["_id"], self.collection, **client)

  def __getitem__(self, name):
    if not name in self.clients:
      self.clients[name] = Client(name, self.collection)
    return self.clients[name]

  def next(self):
    return self.__next__() # pragma: no cover

  def __iter__(self):
    return iter(self.clients.values())

  def delete(self, name):
    logger.info("deleting client info for {0}".format(name))
    try:
      self.clients[name].delete()
      del self.clients[name]
    except KeyError:
      logger.warn("deleting unknown client: {0}".format(name))

  def __contains__(self, name):
    return name in self.clients

class Client(object):
  def __init__(self, name, collection, **kwargs):
    if not name: raise ValueError("name shouldn't be null")
    self.collection = collection
    self.name       = name
    self.queue      = MongoQueue(self.collection, self.name)
    self.schedule   = MongoQueue(self.collection, self.name, "schedule", "schedule")
    self._state     = {}
    self._token     = kwargs["token"]    if "token"    in kwargs else None
    self._location  = kwargs["location"] if "location" in kwargs else None
    self._master    = kwargs["master"]   if "master"   in kwargs else None

    client = self.collection.find_one({"_id": self.name})
    if client is None:
      self.collection.insert_one({
        "_id"     : self.name,
        "state"   : {},
        "queue"   : [],
        "schedule": []
      })
    else:
      self._state    = client["state"]    if "state"    in client else {}
      self._schedule = client["schedule"] if "schedule" in client else []
    self.sid = None
    self.lock = RLock()

  def __iter__(self):
    yield "name",      self.name
    yield "connected", self.connected
    yield "state",     self._state
    yield "queue",     self.queue.items
    yield "location",  self._location
    yield "master",    self._master

  @property
  def connected(self):
    return not self.sid is None

  def update(self, **kwargs):
    with self.lock:
      self.collection.update_one(
        { "_id": self.name },
        { "$set": kwargs }
      )
      if "token"    in kwargs: self._token    = kwargs["token"]
      if "location" in kwargs: self._location = kwargs["location"]
      if "master"   in kwargs: self._master   = kwargs["master"]

  def delete(self):
    self.collection.delete_one({"_id": self.name})

  @property
  def state(self):
    with self.lock:
      return self._state

  @state.setter
  def state(self, new_state):
    with self.lock:
      self.collection.update_one(
        { "_id": self.name },
        { "$set": { "state" : new_state } }
      )
      self._state = new_state

  @property
  def token(self):
    return self._token

  @token.setter
  def token(self, new_token):
    if new_token == self._token: return
    with self.lock:
      self.collection.update_one(
        { "_id": self.name },
        { "$set": { "token" : new_token } }
      )
      self._token = new_token

  @property
  def location(self):
    return self._location

  @location.setter
  def location(self, new_location):
    if new_location == self._location: return
    with self.lock:
      self.collection.update_one(
        { "_id": self.name },
        { "$set": { "location" : new_location } }
      )
      self._location = new_location

  @property
  def master(self):
    return self._master

  @master.setter
  def master(self, new_master):
    if new_master == self._master: return
    with self.lock:
      self.collection.update_one(
        { "_id": self.name },
        { "$set": { "master" : new_master } }
      )
      self._master = new_master

clients = Clients(db.clients)
