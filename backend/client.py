import os
import sys
import argparse
import requests
import logging
import time
import json
import socket
import traceback

from backend import HOSTNAME

try:
  from urllib.parse import urlparse
except ImportError:
  from urlparse import urlparse

import paho.mqtt.client as mqtt

class base(object):
  def __init__(self, name=HOSTNAME, description=None):
    logging.info("client endpoint starting...")
    self.name = name
    if description is None:
      description = self.name + ": a baseAdmin client."

    self.parser = argparse.ArgumentParser(description=description)
    self.parser.add_argument(
      "--cloud",  type=str, help="cloud url.",
      default=os.environ.get("CLOUD_URL")
    )
    self.parser.add_argument(
      "--master",  type=str, help="master url.",
      default=os.environ.get("BACKEND_URL")
    )
    self.parser.add_argument(
      "--mqtt", type=str, help="mqtt url",
      default=os.environ.get("MQTT_URL")
    )
    self.subscription_callbacks = {}

  def start(self):
    self.args = self.parser.parse_args()
    self.process_arguments()
    self.mqtt_client = None
    self.connect_mqtt()

  def process_arguments(self):
    # configure Client from envionment variables or command line arguments
    self.cloud   = None if self.args.cloud   is None else urlparse(self.args.cloud)
    self.master  = None if self.args.master  is None else urlparse(self.args.master)
    self.mqtt    = None if self.args.mqtt    is None else urlparse(self.args.mqtt)

    # if no MQ configuration provided, try to find one
    if self.mqtt is None: self.get_mqtt_connection_details()

  def get_mqtt_connection_details(self):
    if not self.cloud:
      logging.warn("can't fetch master information without cloud URL.")
      return
    self.mqtt = None
    client    = None
    master    = None
    try:
      logging.debug("requesting master IP from " + self.cloud.geturl())
      response = requests.get(
        self.cloud.scheme + "://" + self.cloud.netloc + "/api/client/" + HOSTNAME,
        auth=(self.cloud.username, self.cloud.password),
        timeout=10
      )
      if response.status_code != requests.codes.ok:
        logging.error("request for master IP failed: " + str(response.status_code))
        return
      client = response.json()
      master = client["master"]
      # TODO: make more generic with auth, port,...
      # auth   = ""
      # if m["username"] and m["password"]:
      #   auth = m["username"] + ":" + m["password"] + "@"
      url = "mqtt://" + master["ip"] + ":1883"
      self.mqtt = urlparse(url)
      logging.debug("acquired MQTT URL: " + self.mqtt.geturl())
      # TODO review this regarding configured master info
      #      and take into account
      self.master = urlparse("http://" + master["ip"])
    except Exception as e:
      logging.error("failed to determine MQTT configuration...")
      logging.error("  cloud response: " + str(client))
      logging.error("  exception: " + str(e))

  def connect_mqtt(self):
    if self.mqtt is None:
      logging.warning("client: no MQTT configuration available!")
      return

    try:
      clientId = self.name + "@" + socket.gethostname()
      self.mqtt_client = mqtt.Client(userdata=clientId)
      if self.mqtt.username and self.mqtt.password:
        self.mqtt_client.username_pw_set(self.mqtt.username, self.mqtt.password)
      self.mqtt_client.on_connect    = self.on_connect
      self.mqtt_client.on_disconnect = self.on_disconnect
      self.mqtt_client.on_message    = self.on_message
      self.mqtt_client.on_subscribe  = self.on_subscribe
      last_will = self.last_will_message()
      if last_will:
        self.mqtt_client.will_set(last_will["topic"], last_will["message"], 1, False)
      logging.debug("connecting to MQ " + self.mqtt.netloc)
      self.mqtt_client.connect(self.mqtt.hostname, self.mqtt.port)
      self.mqtt_client.loop_start()
    except Exception as e:
      logging.error("failed to connect to MQTT: " + str(e))
      self.mqtt_client = None

  def on_connect(self, client, clientId, flags, rc):
    logging.debug("client: connected with result code " + str(rc) + " as " + clientId)

  def on_disconnect(self, client, userData, rc):
    logging.error("client: MQTT broker disconnected")
    self.mqtt_client.loop_stop()
    self.mqtt_client = None

  def last_will_message(self):
    return None

  def on_message(self, client, clientId, msg):
    topic = msg.topic
    msg   = str(msg.payload.decode("utf-8"))
    logging.debug("received message: " + topic + " : " + msg)
    self.handle_mqtt_message(topic, msg)

  def handle_mqtt_message(self, topic, msg):
    pass

  def follow(self, topic, callback=None):
    if self.mqtt_client is None: return
    logging.debug("following " + topic)
    (result, mid) = self.mqtt_client.subscribe(topic)
    if not callback is None:
      self.subscription_callbacks[mid] = callback
    return self

  def on_subscribe(self, client, userdata, mid, granted_qos):
    if mid in self.subscription_callbacks:
      self.subscription_callbacks[mid]()
      del self.subscription_callbacks[mid]

  def unfollow(self, topic):
    if self.mqtt_client is None: return
    logging.info("unfollowing " + topic)
    self.mqtt_client.unsubscribe(topic)
    return self

  def publish(self, topic, message):
    if self.mqtt_client is None:
      logging.error("tried to sent MQTT message before connected")
      return
    self.mqtt_client.publish(topic, message,  1, False)
    logging.debug("sent message: " + topic + " : " + message)

  def fail(self, reason, e=None):
    msg = { "message" : reason }
    if e:
      logging.error(reason + ":" + str(e))
      msg["exception"] = traceback.format_exc()
    else:
      logging.error(reason)
      
    self.publish(
      "client/" + self.name + "/errors",
      json.dumps(msg)
    )
