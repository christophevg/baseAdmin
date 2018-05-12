import os
import os.path
import sys
import logging
from functools import reduce
import time
import copy
import hashlib
from tempfile import NamedTemporaryFile
import copy
import time
import operator
import dateutil.parser
import datetime
import pickle

import client

class Storable(object):
  def __init__(self, location,
               on_group_join=None, on_group_leave=None,
               on_service_add=None, on_service_remove=None,
               on_service_update=None, on_service_action=None):
    self.location = location
    self.on_group_join     = on_group_join
    self.on_group_leave    = on_group_leave
    self.on_service_add    = on_service_add
    self.on_service_remove = on_service_remove
    self.on_service_update = on_service_update
    self.on_service_action = on_service_action
    self.config   = {
      "last-message" : None,
      "groups"       : [],
      "services"     : {},
      "scheduled"    : []
    }

    if not os.path.exists(self.location):
      try:
        logging.info("persisting initial configuration to " + self.location)
        self.persist()
      except Exception as e:
        logging.error("could not persist initial configuration: " + str(e))
    else:
      try:
        self.load()
        logging.info("loaded persisted configuration: " + str(self.config))
      except Exception as e:
        logging.error("could not load persisted configuration: " + str(e))

  def update(self, update):
    service = update["service"]
    if not "location" in update and not "groups" in update:
      self.remove_service(service)
    else:
      if "location" in update:
        self.add_service(service, update["location"])
      if "groups" in update:
        self.update_groups(service, update["groups"])
    self.config["last-message"] = update["uuid"]
    self.persist()

  def add_service(self, service, location):
    if service in self.config["services"]:
      logging.warn("not readding already configured service " + service)
      return
    self.config["services"][service] = {
      "location" : location,
      "config"   : {}
    }
    if self.on_service_add: self.on_service_add(service)
  
  def remove_service(self, service):
    if not service in self.config["services"]:
      logging.warn("not removing unconfigured service " + service)
      return
    self.config["services"].pop(service, None)
    if self.on_service_remove: self.on_service_remove(service)

  def update_groups(self, services, groups):
    required = set(groups)
    if self.on_group_leave:
      deprecated = list(set(self.config["groups"]) - set(required))
      for group in deprecated:
        self.on_group_leave(group)
    if self.on_group_join:
      additional = list(set(required) - set(self.config["groups"]))
      for group in additional:
        self.on_group_join(group)
    self.config["groups"] = list(required)

  def update_service(self, service, update):
    if "valid-from" in update:
      schedule = dateutil.parser.parse(update["valid-from"]) # parse datetime
      self.schedule(service, schedule, update)
    else:
      self.apply(service, update)
    self.config["last-message"] = update["uuid"]
    self.persist()

  def schedule(self, service, schedule, update):
    self.config["scheduled"].append({
      "service"  : service,
      "schedule" : schedule,
      "update"   : update
    })
    self.config["scheduled"].sort(key=operator.itemgetter("schedule"))
    logging.info("scheduled update for " + service + " in " + str((schedule - datetime.datetime.now()).total_seconds()) + "s")
    return False

  def handle_scheduled(self):
    now     = datetime.datetime.now()
    while len(self.config["scheduled"]) > 0 and self.config["scheduled"][0]["schedule"] <= now:
      s = self.config["scheduled"][0]
      logging.info("performing scheduled update for " + s["service"])
      self.apply(s["service"], s["update"])
      del self.config["scheduled"][0]
      self.persist()

  def apply(self, service, update):
    try:
      self.on_service_action(service, update["action"])
    except KeyError:
      try:
        # for now we do 1-level k/v updates
        for k in update["config"]:
          self.config["services"][service]["config"][k] = update["config"][k]
        self.on_service_update(service)
      except KeyError:
        logging.warn("can't update unknown service: " + service)        
    except:
      logging.error("unknown update: " + str(update))

  def get_last_message_id(self):
    return self.config["last-message"]

  def list_groups(self):
    return self.config["groups"]

  def list_services(self):
    return list(self.config["services"].keys())

  def get_service_location(self, service):
    try:
      return self.config["services"][service]["location"]
    except KeyError:
      raise Exception("unknown service: " + service)    

  def get_service_configuration(self, service):
    try:
      return self.config["services"][service]["config"]
    except KeyError:
      raise Exception("unknown service: " + service)
  
  def persist(self):
    config = copy.deepcopy(self.config)
    config["checksum"] = self.hash(config)
    with NamedTemporaryFile(mode="wb+", delete=False) as fp:
      pickle.dump(config, fp, protocol=2)
    try:
      self.check(fp.name)
      path = os.path.dirname(self.location)
      if not os.path.exists(path): os.makedirs(path)
      os.rename(fp.name, self.location)
    except Exception as e:
      raise Exception("generated config file is invalid: " + fp.name + ", due to: " + str(e))
    logging.debug("persisted configuration")

  def load(self):
    with open(self.location, "rb") as fp:
      config = pickle.load(fp)
      try:
        self.validate(config)
        self.config = config
      except Exception as e:
        raise Exception("config is not valid: " + self.location + ", due to: " + str(e))

  def check(self, f):
    with open(f, "rb") as fp:
      config = pickle.load(fp)
      self.validate(config)

  def validate(self, config):
    expected = config["checksum"]
    config.pop("checksum", None)
    computed = self.hash(config)
    assert expected == computed, "checksums don't match: expected {}, got {}".format(expected, computed)
    return True

  def hash(self, config):
    bs = pickle.dumps(config)
    h  = hashlib.md5(bs).hexdigest()
    return h
