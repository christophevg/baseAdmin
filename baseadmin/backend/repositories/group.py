import logging
logger = logging.getLogger(__name__)

from threading import RLock

class Groups(object):
  def __init__(self, collection):
    self.collection = collection
    self.groups = {}
    # load all groups
    for group in self.collection.find():
      self.groups[group["_id"]] = Group(group["_id"], self.collection, group["members"])

  def __getitem__(self, name):
    if not name in self.groups: self.groups[name] = Group(name, self.collection)
    return self.groups[name]

  def __iter__(self):
    for name in self.groups:
      yield name, list(self.groups[name])

  def delete(self, name):
    logger.info("deleting group {0}".format(name))
    try:
      self.groups[name].delete()
      del self.groups[name]
    except KeyError:
      logger.warn("deleting unknown group: {0}".format(name))

  def __contains__(self, name):
    return name in self.groups

class Group(object):
  def __init__(self, name, collection, members=[]):
    self.name       = name
    self.collection = collection
    self._members   = members
    self.lock       = RLock()
    
    group = self.collection.find_one({"_id": self.name})
    if group is None:
      self.collection.insert_one({
        "_id"     : self.name,
        "members" : self._members
      })

  def __len__(self):
    return len(self._members)

  def __iter__(self):
    return iter(self._members)

  def delete(self):
    self.collection.delete_one({ "_id": self.name })

  def add(self, member):
    with self.lock:
      self.collection.update(
        { "_id": self.name },
        { "$addToSet" : { "members" : member } }
      )
      if not member in self._members:
        self._members.append(member)

  def remove(self, member):
    with self.lock:
      if len(self._members) > 0:
        self.collection.update(
          { "_id"   : self.name },
          { "$pull" : { "members" : member } }
        )
        self._members.remove(member)
