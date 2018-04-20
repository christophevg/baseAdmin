import os
import os.path
import sys
import logging
from functools import reduce

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
      self.save()
    else:
      self.load()

  def update(self, config):
    logging.debug("persisting config update")
    self.config = config
    self.save()

  def current(self):
    return self.config

  def save(self):
    self.config["checksum"] = self.hash(self.config)
    # generate temp file
    fp = NamedTemporaryFile(mode="w+", delete=False)
    json.dump(self.config, fp)
    fp.close()
    # check temp file
    if self.check(fp.name):
      # ensure parent path exists
      path = os.path.dirname(self.location)
      if not os.path.exists(path):
        os.makedirs(path)
      os.rename(fp.name, self.location)
    else:
      logging.error("failed to store configuration as " + fp.name)
      raise IOError("failed to store configuration")

  def load(self):
    with open(self.location) as fp:
      config = json.load(fp)
      if self.isValid(config):
        self.config = config
      else:
        logging.error("failed to load configuration from " + self.location)

  def check(self, f):
    with open(f) as fp:
      config = json.load(fp)
      return self.isValid(config)

  def isValid(self, config):
    try:
      expected = config["checksum"]
      config.pop("checksum")
      computed = self.hash(config)
      assert expected == computed
    except Exception as e:
      logging.error(str(e))
      return False
    return True

  def hash(self, config):
    if len(config) < 1: return 0
    return reduce(lambda x,y : x^y, [hash(item) for item in config.items()])

# Create global Store object

CONFIG_STORE = os.environ.get("CONFIG_STORE")
if not CONFIG_STORE:
  CONFIG_STORE = "/opt/baseAdmin/config.json"

store = Storable(CONFIG_STORE)
