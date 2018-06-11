import os
import logging

from backend.store import store
import backend.config

class StoreBased(backend.config.Config):
  def __init__(self, client, *args, **kwargs):
    self.client = client
    super(self.__class__, self).__init__(*args, **kwargs)
  
  def initialize_persistence(self):
    try:
      self.load()
    except KeyError:
      logging.info("persisting initial configuration for " + self.client)
      self.persist()

  def persist(self):
    store.config.update_one(
      { "_id": self.client },
      { "$set" : self.config },
      upsert=True
    )
    logging.debug("persisted configuration for " + self.client)

  def load(self):
    config = store.config.find_one({ "_id" : self.client}, {"_id": False})
    if config is None:
      raise KeyError("unknown client " + self.client)
    self.config = config
    logging.debug("loaded client configuration for " + self.client)

class Collection(object):
  def __init__(self):
    self.configs = {}

  def handle_mqtt_update(self, topic, update):
    client = topic.split("/")[1]
    self[client].handle_mqtt_update(topic, update)

  def __getitem__(self, client):
    if not client in self.configs:
      logging.debug("lazy-loading config for " + client)
      self.configs[client] = StoreBased(client)
    # FIXME: is this the best place to handle scheduled updates?
    #        rationale: StoreBased configs don't trigger on_* handlers
    #        and "only" need to be in sync with scheduled updates on access
    #        this is the "on access" entry point
    self.configs[client].handle_scheduled()
    return self.configs[client]
