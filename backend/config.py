import os
import os.path
import sys
import logging
import copy
import hashlib
from tempfile import NamedTemporaryFile
import time
import operator
import dateutil.parser
import datetime
import pickle

class Config(object):
  def __init__(self, on_group_join=None, on_group_leave=None,
               on_service_add=None, on_service_remove=None,
               on_service_update=None, on_service_action=None):
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
    self.initialize_persistence()

  '''
    Updates to the configuration mimic the configuration structure:
      entire config:    .../<id>
      all services:     .../<id>/services
      all groups:       .../<id>/groups
      single service    .../<id>/service/<name>
  '''
  def handle_mqtt_update(self, topic, update):
    parts  = topic.split("/")
    if len(parts) > 3 and parts[2] == "service":
      service = parts[3]
      self.__update_service(service, update)
    elif len(parts) > 2 and parts[2] == "services":
      self.__replace_services(update)
    elif len(parts) > 2 and parts[2] == "groups":
      self.__update_groups(update)
    elif len(parts) == 2:
      self.__update(update)
    else:
      logging.error("received unhandled topic: " + topic)

  def handle_scheduled(self):
    now = datetime.datetime.now()
    while len(self.config["scheduled"]) > 0 and self.config["scheduled"][0]["schedule"] <= now:
      s = self.config["scheduled"][0]
      logging.info("performing scheduled update for " + s["service"])
      self.__apply(s["service"], s["update"])
      del self.config["scheduled"][0]
      self.persist()

  @property
  def last_message_id(self):
    return self.config["last-message"]

  @property
  def groups(self):
    return self.config["groups"]

  @property
  def services(self):
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

  # "abstract" methods to implement different ways to persist the config

  def initialize_persistence(self):
    pass
  
  def persist(self):
    pass

  def load(self):
    pass

  def __update(self, update):
    self.config["last-message"] = update["last-message"]
    self.__update_groups(update["groups"])
    self.__update_services(update["services"])
    self.config["scheduled"] = update["scheduled"]
    self.persist()

  def __update_services(self, update):
    # remove deprecated services
    deprecated = list(set(self.config["services"].keys()) - set(update["services"].keys()))
    for service in deprecated:
      self.__remove_service(service)
    # add new services
    additional = list(set(update["services"].keys() - set(self.config["services"].keys())))
    for service in additional:
      self.__add_service(service, update["services"][service]["location"])
    # update (remaining) existing (and new) services
    for service in update["services"]:
      self.config["services"][service]["config"] = update["services"][service]["config"]
      if self.on_service_update:
        self.on_service_update(service)

  def __replace_services(self, update):
    services = {}
    for service in update["services"]:
      services[service["name"]] = {
        "location" : service["location"],
        "config" : None
      }
    logging.debug("new service configuration: " + str(services))
    self.__update_services({"services" : services })
    self.config["last-message"] = update["uuid"]
    self.persist()

  def __update_service(self, service, update):
    logging.debug("updating service config for " + service)
    if "valid-from" in update:
      schedule = dateutil.parser.parse(update["valid-from"]) # parse datetime
      self.__schedule(service, schedule, update)
    else:
      self.__apply(service, update)
    self.config["last-message"] = update["uuid"]
    self.persist()

  def __add_service(self, service, location):
    if service in self.config["services"]:
      logging.warn("not re-adding already configured service " + service)
      return
    self.config["services"][service] = {
      "location" : location,
      "config"   : {}
    }
    logging.debug("added service " + service)
    if self.on_service_add: self.on_service_add(service)
  
  def __remove_service(self, service):
    if not service in self.config["services"]:
      logging.warn("not removing unconfigured service " + service)
      return
    self.config["services"].pop(service, None)
    logging.debug("removed service " + service)
    if self.on_service_remove: self.on_service_remove(service)

  def __update_groups(self, groups):
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

  def __schedule(self, service, schedule, update):
    self.config["scheduled"].append({
      "service"  : service,
      "schedule" : schedule,
      "update"   : update
    })
    self.config["scheduled"].sort(key=operator.itemgetter("schedule"))
    logging.info("scheduled update for " + service + " in " + str((schedule - datetime.datetime.now()).total_seconds()) + "s")
    return False

  def __apply(self, service, update):
    if "action" in update:
      if self.on_service_action:
        self.on_service_action(service, update["action"])
      else:
        logging.warn("no service action handler defined")
    elif "config" in update:
      try:
        # for now we do 1-level k/v updates
        for k in update["config"]:
          self.config["services"][service]["config"][k] = update["config"][k]
        if self.on_service_update:
          self.on_service_update(service)
      except KeyError:
        logging.warn("can't update unknown service: " + service)        
    else:
      logging.error("unknown update: " + str(update))

class FileBased(Config):
  def __init__(self, location, *args, **kwargs):
    self.location = location
    super(self.__class__, self).__init__(*args, **kwargs)

  def initialize_persistence(self):
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
