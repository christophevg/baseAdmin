import os
import sys
import argparse
import requests
import logging
from urllib.parse import urlparse

import paho.mqtt.client as mqtt

from local import HOSTNAME, IP

import logging

class Base():
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

    args = parser.parse_args()

    # configure Client from envionment variables or command line arguments
    self.backend = None if args.backend is None else urlparse(args.backend)
    self.mqtt    = None if args.mqtt    is None else urlparse(args.mqtt)

    # if no MQ configuration provided, try to fetch it from the backend
    if self.mqtt is None: self.get_mqtt_connection_details()

    self.mqtt_client = None

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

  def run(self):
    logging.info("starting client run")
    self.connect_mqtt()
    return True

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

  def on_message(self, client, clientId, msg):
    topic = msg.topic
    msg   = str(msg.payload.decode("utf-8"))
    self.handle_mqtt_message(topic, msg)

  def handle_mqtt_message(self, topic, msg):
    pass

  def follow(self, topic):
    if self.mqtt_client is None: return
    logging.debug("following MQTT: " + topic)
    self.mqtt_client.subscribe(topic)

  def publish(self, topic, message):
    self.mqtt_client.publish(topic, message,  1, False)
