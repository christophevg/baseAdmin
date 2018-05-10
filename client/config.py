import os
import os.path
import sys
import logging
from functools import reduce
import time
import copy
import hashlib
from tempfile import NamedTemporaryFile
import json
import copy
import time
import operator
import dateutil.parser
import datetime

import client

class Storable(object):
  def __init__(self, location):
    self.location = location
    self.config   = {
      "last-message" : None,
      "services" : {},
      "scheduled"  : []
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
    changed = False
    if "location" in update:
      changed = self.add_service(update["service"], update["location"])
    else:
      changed = self.remove_service(update["service"])
    self.config["last-message"] = update["uuid"]
    self.persist()
    return changed

  def add_service(self, service, location):
    self.config["services"][service] = {
      "location" : location,
      "config"   : {}
    }
    return True
  
  def remove_service(self, service):
    if not service in self.config["services"]:
      logging.warn("not removing unconfigured service " + service)
      return False
    self.config["services"].pop(service, None)
    return True

  def update_service(self, service, update):
    changed = False
    if "valid-from" in update:
      schedule = update["valid-from"]
      try:
        schedule = int(schedule) # epoch seconds
      except ValueError:
        schedule = dateutil.parser.parse(schedule) # parse datetime
        schedule = (schedule - datetime.datetime(1970,1,1)).total_seconds()
      changed = self.schedule(service, schedule, update["config"])
    else:
      changed = self.apply(service, update["config"])
    self.config["last-message"] = update["uuid"]
    self.persist()
    logging.debug("changed=" + str(changed))
    return changed

  def schedule(self, service, schedule, update):
    self.config["scheduled"].append({
      "service"  : service,
      "schedule" : schedule,
      "update"   : update
    })
    self.config["scheduled"].sort(key=operator.itemgetter("schedule"))
    logging.info("scheduled update for " + service + " in " + str(schedule - time.time()) + "s")
    return False

  def handle_scheduled(self):
    changed = set()
    now     = time.time()
    while len(self.config["scheduled"]) > 0 and self.config["scheduled"][0]["schedule"] <= now:
      s = self.config["scheduled"][0]
      logging.info("performing scheduled update for " + s["service"])
      self.apply(s["service"], s["update"])
      changed.add(s["service"])
      del self.config["scheduled"][0]
      self.persist()
    return changed

  def apply(self, service, update):
    try:
      # for now we do 1-level k/v updates
      for k in update:
        self.config["services"][service]["config"][k] = update[k]
      return True
    except KeyError:
      logging.warn("can't update unknown service: " + service)
      return False

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
    with NamedTemporaryFile(mode="w+", delete=False) as fp:
      json.dump(config, fp, indent=2, sort_keys=True)
    try:
      self.check(fp.name)
      path = os.path.dirname(self.location)
      if not os.path.exists(path): os.makedirs(path)
      os.rename(fp.name, self.location)
    except Exception as e:
      raise Exception("generated config file is invalid: " + fp.name + ", due to: " + str(e))
    logging.debug("persisted configuration")

  def load(self):
    with open(self.location) as fp:
      config = json.load(fp)
      try:
        self.validate(config)
        self.config = config
      except Exception as e:
        raise Exception("config is not valid: " + self.location + ", due to: " + str(e))

  def check(self, f):
    with open(f) as fp:
      config = json.load(fp)
      self.validate(config)

  def validate(self, config):
    expected = config["checksum"]
    config.pop("checksum", None)
    computed = self.hash(config)
    assert expected == computed, "checksums don't match: expected {}, got {}".format(expected, computed)
    return True

  def hash(self, config):
    js = json.dumps(config, sort_keys=True)
    h  = hashlib.md5(js.encode()).hexdigest()
    return h
