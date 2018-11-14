# The baseAdmin Store implements an end-point or node within the baseAdmin
# network as a service. It connects to the baseAdmin network and monitors all
# messages. It tracks the configuration of all clients and replays messages
# when it notices that a client comes online and has missed certain messages.

import os
import logging
import time
import json
import copy
import datetime
import importlib

import backend.client

from backend.store         import store, config
from backend.store.plugins import Monitor
from backend.store.plugins import *

class Runner(backend.client.base):
  
  def __init__(self, *args, **kwargs):
    super(self.__class__, self).__init__(*args, **kwargs)
    self.monitors = []
    self.load_monitors()
  
  def load_monitors(self):
    for monitor in Monitor.__subclasses__():
      self.monitors.append(monitor(store, self))

  def start(self):
    super(self.__class__, self).start()
    logging.info("starting monitoring loop...")
    try:
      while(True):
        time.sleep(1)
    except KeyboardInterrupt:
      logging.info("shutting down")
      pass
  
  def on_connect(self, client, clientId, flags, rc):
    logging.info("connected to MQTT")
    super(self.__class__, self).on_connect(client, clientId, flags, rc)
    following = set()
    for monitor in self.monitors:
      for topic in monitor.follows():
        if not topic in following:
          self.follow(topic)
          following.add(topic)

  def handle_mqtt_message(self, topic, message):
    try:
      message = json.loads(message)
    except Exception as e:
      self.fail("couldn't parse JSON message", e)
      return

    try:
      topic = topic.split("/")
      for monitor in self.monitors:
        monitor.handle(topic, message)
    except Exception as e:
      self.fail("failed to handle message", e)

class StatusMonitor(Monitor):
  def follows(self):
    return [ "client/+" ]

  def handle(self, topic, status):
    if len(topic) != 2: return
    client = topic[1]

    # track status
    if "status" in status:
      self.store.status.update_one(
        { "_id": client },
        { "$set" : status },
        upsert=True
      )

class ErrorMonitor(Monitor):
  def follows(self):
    return [ "client/+/errors" ]
    
  def handle(self, topic, error):
    if len(topic) != 3 or topic[2] != "errors": return
    client = topic[1]

    self.store.errors.insert_one({
      "client" : client,
      "error"  : error,
      "ts"     : datetime.datetime.utcnow()
    })

class ConfigMonitor(Monitor):
  def __init__(self, *args, **kwargs):
    super(self.__class__, self).__init__(*args, **kwargs)
    self.configs = config.Collection()

  def follows(self):
    return [
      "client/+",
      "client/+/services",
      "client/+/groups",
      "group/+/services",
      "client/+/service/+",
      "group/+/service/+"
    ]

  def handle(self, topic, message):
    if len(topic) == 2:
      client = topic[1]
      # send latest version if reported config version is different
      if "status" in message and message["status"] == "online":
        if "config" in message:
          if self.configs[client].last_message_id != message["config"]:
            logging.info("sending config to outdated client: " + client)
            config = copy.deepcopy(self.configs[client].config)
            config.pop("_id", None)
            self.mqtt.publish("client/" + client, json.dumps(config))
          else:
            if self.configs[client].last_message_id is None:
              if not self.configs["__default__"].last_message_id is None:
                logging.info("sending default config to client: " + client)
                self.configs[client].config = copy.deepcopy(self.configs["__default__"].config)
                self.configs[client].persist()
                config = copy.deepcopy(self.configs[client].config)
                config.pop("_id", None)
                self.mqtt.publish("client/" + client, json.dumps(config))
      
    if (len(topic) == 3 and topic[2] == "services") or\
       (len(topic) == 4 and topic[2] == "service")  or\
       (len(topic) == 3 and topic[2] == "groups"):
      self.configs.handle_mqtt_update("/".join(topic), message)
