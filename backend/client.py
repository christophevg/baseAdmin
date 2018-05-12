import os
import sys
import argparse
import requests
import logging
import time
from urllib.parse import urlparse
import json
import socket
import traceback

import paho.mqtt.client as mqtt

class base(object):
  def __init__(self, name="client", description=None):
    self.name = name
    if description is None:
      description = self.name + ": a baseAdmin client."

    self.parser = argparse.ArgumentParser(description=description)
    self.parser.add_argument(
      "--backend",  type=str, help="backend url.",
      default=os.environ.get("BACKEND_URL")
    )
    self.parser.add_argument(
      "--mqtt", type=str, help="mqtt url",
      default=os.environ.get("MQTT_URL")
    )

  def start(self):
    self.args = self.parser.parse_args()
    self.process_arguments()
    self.mqtt_client = None
    self.connect_mqtt()

  def process_arguments(self):
    # configure Client from envionment variables or command line arguments
    self.backend = None if self.args.backend is None else urlparse(self.args.backend)
    self.mqtt    = None if self.args.mqtt    is None else urlparse(self.args.mqtt)

    # if no MQ configuration provided, try to fetch it from the backend
    if self.mqtt is None: self.get_mqtt_connection_details()

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

    clientId = self.name + "@" + socket.gethostname()
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
  
  def on_message(self, client, clientId, msg):
    topic = msg.topic
    msg   = str(msg.payload.decode("utf-8"))
    logging.debug("received message: " + topic + " : " + msg)
    self.handle_mqtt_message(topic, msg)

  def handle_mqtt_message(self, topic, msg):
    pass

  def follow(self, topic):
    if self.mqtt_client is None: return
    logging.info("following " + topic)
    self.mqtt_client.subscribe(topic)
    return self

  def unfollow(self, topic):
    if self.mqtt_client is None: return
    logging.info("unfollowing " + topic)
    self.mqtt_client.unsubscribe(topic)
    return self

  def publish(self, topic, message):
    self.mqtt_client.publish(topic, message,  1, False)
    logging.debug("sent message: " + topic + " : " + message)

  def fail(self, message, e=None):
    logging.error(message + " : " + str(e))
    self.publish(
      "client/" + self.name + "/errors",
      json.dumps({
        "message" : message,
        "exception" : ''.join(traceback.format_exception(type(e), e, e.__traceback__))
      })
    )
