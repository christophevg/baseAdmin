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

import client

class Storable(object):
  def __init__(self, location):
    self.location = location
    self.config   = {
      "ts" : 0,
      "services" : {}
    }
    if not os.path.exists(self.location):
      try:
        logging.info("persisting initial configuration to " + self.location)
        self.save()
      except Exception as e:
        logging.error("could not persist initial configuration: " + str(e))
    else:
      try:
        self.load()
        logging.info("loaded persisted configuration: " + str(self.config))
      except Exception as e:
        logging.error("could not load persisted configuration: " + str(e))

  def add_service(self, service, location, ts=None):
    self.config["services"][service] = {
      "location" : location,
      "config"   : {}
    }
    self.config["ts"] = ts if not ts is None else time.time()
    self.persist()
  
  def remove_service(self, service, ts=None):
    if not service in self.config["services"]:
      logging.warn("not removing unconfigured service " + service)
      return
    self.config["services"].pop(service, None)
    self.config["ts"] = ts if not ts is None else time.time()
    self.persist()

  def update_service_configuration(self, service, update, ts=None):
    try:
      # for now we do 1-level k/v updates
      for k in update:
        self.config["services"][service]["config"][k] = update[k]
      self.config["ts"] = ts if not ts is None else time.time()
      self.persist()
    except KeyError:
      raise Exception("unknown service: " + service)

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
