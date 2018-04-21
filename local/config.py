import os
import os.path
import sys
import logging
from functools import reduce
import time
import copy
import hashlib

from os.path import join, dirname, isfile
from dotenv import load_dotenv

script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
dotenv_path = join(script_path, "env.local")
if isfile(dotenv_path):
  logging.info("loading local environment configuration from " + dotenv_path)
  load_dotenv(dotenv_path)

import local.logging

from tempfile import NamedTemporaryFile
import json

class Storable(object):
  def __init__(self, location):
    self.location = location
    self.config   = {}
    if not os.path.exists(self.location):
      try:
        self.save()
        logging.info("initialised persisted configuration")
      except Exception as e:
        logging.error("could not persist initial configuration: " + str(e))
    else:
      try:
        self.load()
        logging.info("loaded persisted configuration: " + str(self.config))
      except Exception as e:
        logging.error("could not load persisted configuration: " + str(e))

  def update(self, config):
    self.config = config
    try:
      self.save()
      logging.info("persisted new configuration: " + str(self.config))
    except Exception as e:
      logging.error("could not persist new configuration: " + str(e))

  def current(self):
    return self.config

  def save(self):
    if not "ts" in self.config: self.config["ts"] = time.time()
    self.config["checksum"] = self.hash(self.config)
    fp = NamedTemporaryFile(mode="w+", delete=False)
    json.dump(self.config, fp, indent=2, sort_keys=True)
    fp.close()
    try:
      self.check(fp.name)
      path = os.path.dirname(self.location)
      if not os.path.exists(path): os.makedirs(path)
      os.rename(fp.name, self.location)
    except Exception as e:
      raise Exception("generated config file is invalid: " + fp.name + ", due to: " + str(e))

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
    config.pop("checksum")
    computed = self.hash(config)
    assert expected == computed, "checksums don't match: expected {}, got {}".format(expected, computed)
    return True

  def hash(self, config):
    js = json.dumps(config, sort_keys=True)
    h  = hashlib.md5(js.encode()).hexdigest()
    return h

# Create global Store object

CONFIG_STORE = os.environ.get("CONFIG_STORE")
if not CONFIG_STORE:
  CONFIG_STORE = "/opt/baseAdmin/config.json"

store = Storable(CONFIG_STORE)
