import os
import sys
import argparse
import requests
import logging
import time
from urllib.parse import urlparse
import json

import paho.mqtt.client as mqtt

from servicefactory import Service

from local import HOSTNAME, IP

import local.config
import local.logging

class base(object):
  def __init__(self, name="client", description=None):
    self.name = name
    if description is None:
      description = self.name + ": a baseAdmin client."

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
      "--backend",  type=str, help="backend url.",
      default=os.environ.get("BACKEND_URL")
    )
    parser.add_argument(
      "--mqtt", type=str, help="mqtt url",
      default=os.environ.get("MQTT_URL")
    )
    parser.add_argument(
      "--config", type=str, help="configuration",
      default=os.environ.get("CONFIG_STORE")
    )

    args = parser.parse_args()

    # configure Client from envionment variables or command line arguments
    self.backend = None if args.backend is None else urlparse(args.backend)
    self.mqtt    = None if args.mqtt    is None else urlparse(args.mqtt)

    # if no MQ configuration provided, try to fetch it from the backend
    if self.mqtt is None: self.get_mqtt_connection_details()

    self.mqtt_client = None
    self.connect_mqtt()

    self.config  = local.config.Storable(
      "/opt/baseAdmin/config.json" if args.config  is None else args.config
    )

  def get_mqtt_connection_details(self):
    if not self.backend: return

    logging.info("requesting MQ connection details from " + self.backend.geturl())
    response = requests.get(
      self.backend.scheme + ":" + self.backend.netloc + "/api/mq/connection/mqtt",
      auth=(self.backend.username, self.backend.password)
    )

    if response.status_code != requests.codes.ok:
      logging.error("request for MQ connection details failed: " + str(response.status_code))
      return

    self.mq = response.json()

  def connect_mqtt(self):
    if self.mqtt is None:
      logging.warning("no MQTT configuration available!")
      return

    clientId = self.name + "@" + HOSTNAME + "(" + IP + ")"
    self.mqtt_client = mqtt.Client(userdata=clientId)
    if self.mqtt.username and self.mqtt.password:
      self.mqtt_client.username_pw_set(self.mqtt.username, self.mqtt.password)
    self.mqtt_client.on_connect = self.on_connect
    self.mqtt_client.on_message = self.on_message
    self.mqtt_client.will_set("client/" + self.name + "/status", "offline", 1, False)
    logging.debug("connecting to MQ " + self.mqtt.netloc)
    self.mqtt_client.connect(self.mqtt.hostname, self.mqtt.port)
    self.mqtt_client.loop_start()

  def on_connect(self, client, clientId, flags, rc):
    logging.debug("connected with result code " + str(rc))
    self.mqtt_client.publish("client/" + self.name + "/status", "online",  1, False)
    self.subscribe()
  
  def subscribe(self):
    pass

  def on_message(self, client, clientId, msg):
    topic = msg.topic
    msg   = str(msg.payload.decode("utf-8"))
    self.handle_mqtt_message(topic, msg)

  def handle_mqtt_message(self, topic, msg):
    pass

  def follow(self, topic):
    if self.mqtt_client is None: return
    logging.debug("following " + topic)
    self.mqtt_client.subscribe(topic)
    return self

  def publish(self, topic, message):
    self.mqtt_client.publish(topic, message,  1, False)

@Service.API.endpoint(port=17171)
class Service(Service.base, base):
  
  def subscribe(self):
    self.follow("client/" + self.name + "/config")
    # TODO refactor this
    self.handlers = {}

  def handle_mqtt_message(self, topic, msg):
    logging.info("received message: " + topic + " : " + msg)
    try:
      event = json.loads(msg)
      for handler in self.handlers[event["type"]]:
        logging.info("dispatching to " + handler)
        self.post(handler, event)
    except Exception as e:
      logging.error("event handling failed: " + repr(e))

  def loop(self):
    time.sleep(5)

  @Service.API.handle("register_message_handler")
  def handle_register_message_handler(self, data):
    args = json.loads(data)
    event       = args["event"]
    handler_url = args["handler"]
    logging.info("registering handler for " + event + " : " + handler_url)
    try:
      self.handlers[event].append(handler_url)
    except KeyError:
      self.handlers[event] = [ handler_url ]

# TODO
# [ ] implement config changes as events with partial updates
# [ ] notify online + config version
# [ ] config poll loop for events if mqtt not available
# [ ] implement group concept
