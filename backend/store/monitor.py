# The baseAdmin Store implements an end-point or node within the baseAdmin
# network as a service. It connects to the baseAdmin network and monitors all
# messages. It tracks the configuration of all clients and replays messages
# when it notices that a client comes online and has missed certain messages.

import os
import logging
import time
import json
import copy

import backend.client
from backend.store import store
from backend.store import config

class Runner(backend.client.base):
  
  def __init__(self, *args, **kwargs):
    self.configs = config.Collection()
    super(self.__class__, self).__init__(*args, **kwargs)
  
  def start(self):
    super(self.__class__, self).start()
    logging.info("starting loop")
    try:
      while(True):
        time.sleep(1)
    except KeyboardInterrupt:
      logging.info("shutting down")
      pass
  
  def on_connect(self, client, clientId, flags, rc):
    logging.info("connected to MQTT")
    super(self.__class__, self).on_connect(client, clientId, flags, rc)
    self.follow("client/+")           # status (online/offline)

    self.follow("client/+/errors")    # errors

    self.follow("client/+/service/ReportingService/stats") # stats

    self.follow("client/+/services")  # services configuration
    self.follow("group/+/services")

    self.follow("client/+/service/+") # service configurations
    self.follow("group/+/service/+")

  def handle_mqtt_message(self, topic, message):
    message = json.loads(message)
    parts   = topic.split("/")
    
    if len(parts) == 2:
      return self.__handle_status(parts[1], message)

    if len(parts) == 3 and parts[2] == "errors":
      return self.__handle_error(parts[1], message)

    if len(parts) == 5:
      return self.__handle_stats(parts[1], message)
    
    self.configs.handle_mqtt_update(topic, message)

  def __handle_status(self, client, status):
    # track status
    if "status" in status:
      store.status.update_one(
        { "_id": client },
        {
          "$currentDate" : { "lastModified": True, },
           "$set" : { "status" : status["status"] }
         },
        upsert=True
      )
    # send latest version if reported config version is different
    if "config" in status:
      if self.configs[client].last_message_id != status["config"]:
        logging.info("sending latest config to outdated client: " + client)
        config = copy.deepcopy(self.configs[client].config)
        config.pop("_id", None)
        self.publish("client/" + client, json.dumps(config))

  def __handle_error(self, client, error):
    store.errors.insert_one({
      "client" : client,
      "error"  : error
    })

  def __handle_stats(self, client, stats):
    store.system.update_one(
      { "_id": client },
      { "$push"  : { "stats" : {
        "$each"  : [ stats ],
        "$sort"  : { "system_time" : -1 },
        "$slice" : 12
      }}},
      upsert=True
    )
