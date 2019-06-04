import operator

from threading import Lock

class MongoQueue(object):
  def __init__(self, collection, id, queue="queue", sorted=None):
    self.collection = collection
    self.id = id
    self.queue = queue
    self.sorted = sorted

    record = self.collection.find_one({"_id": self.id})
    self._items = record[queue] if record and queue in record else []
    self.lock = Lock()

  def add(self, item):
    return self.append(item)

  def append(self, item):
    with self.lock:
      self._items.append(item)
      if self.sorted: self._items.sort(key=operator.itemgetter(self.sorted))
      self.collection.update_one(
        { "_id": self.id },
        { "$set": { self.queue: self._items } },
        upsert=True
      )
    return self

  @property
  def items(self):
    with self.lock:
      return self._items

  @property
  def empty(self):
    with self.lock:
      return len(self._items) == 0

  def __len__(self):
    with self.lock:
      return len(self._items)

  def get(self):
    with self.lock:
      if len(self._items) > 0:
        return self._items[0]
    return None

  def pop(self):
    with self.lock:
      if len(self._items) > 0:
        self.collection.update(
          {"_id": self.id},
          { "$pop":  { self.queue: -1 }}
        )
        self._items.pop(0)
    return self
