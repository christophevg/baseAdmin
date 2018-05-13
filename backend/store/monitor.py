# The baseAdmin Store implements an end-point or node within the baseAdmin
# network as a service. It connects to the baseAdmin network and monitors all
# messages. It tracks the configuration of all clients and replays messages
# when it notices that a client comes online and has missed certain messages.

import os
import logging
import time
import json

import backend.client
from backend.store import store

class Runner(backend.client.base):
  
  def start(self):
    super(self.__class__, self).start()
    try:
      while(True):
        time.sleep(1)
    except KeyboardInterrupt:
      logging.info("shutting down")
      pass
  
  def on_connect(self, client, clientId, flags, rc):
    super(self.__class__, self).on_connect(client, clientId, flags, rc)
    self.follow("client/+")           # status (online/offline)

    self.follow("client/+/errors")    # errors

    self.follow("client/+/services")  # services configuration
    self.follow("group/+/services")

    self.follow("client/+/service/+") # service configurations
    self.follow("group/+/service/+")
    
    self.follow("client/+/service/ReportingService/stats") # stats

  def handle_mqtt_message(self, topic, message):
    message = json.loads(message)
    parts   = topic.split("/")
    
    if len(parts) == 2:
      self.handle_status(parts[1], message)

    if len(parts) == 3 and parts[2] == "errors":
      self.handle_error(parts[1], message)

  def handle_status(self, client, status):
    # track status
    store.status.update_one(
      { "_id": client },
      { "$set" : { "status" : status["status"] } },
      upsert=True
    )
    # TODO check config version when status is "online"
    # send

  def handle_error(self, client, error):
    store.errors.insert_one({
      "client" : client,
      "error"  : error
    })
