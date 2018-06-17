import os
import sys
import argparse
import requests
import logging
import time
import json
import socket
import traceback
import git

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

    # if no MQ configuration provided, try to fetch it from the cloud or master
    if self.mqtt is None: self.get_mqtt_connection_details()

  def get_mqtt_connection_details(self):
    if not self.cloud:
      logging.warn("can't fetch master information without cloud URL.")
      return
    logging.debug("requesting master IP from " + self.cloud.geturl())
    response = requests.get(
      self.cloud.scheme + "://" + self.cloud.netloc + "/api/client/" + HOSTNAME,
      auth=(self.cloud.username, self.cloud.password)
    )
    if response.status_code != requests.codes.ok:
      logging.error("request for master IP failed: " + str(response.status_code))
      return
    client = response.json()
    if "master" in client:
      master = client["master"]
      # TODO: make more generic with auth, port,...
      # auth   = ""
      # if m["username"] and m["password"]:
      #   auth = m["username"] + ":" + m["password"] + "@"
      url = "mqtt://" + master["ip"] + ":1883"
      self.mqtt = urlparse(url)
      logging.debug("acquired MQTT URL: " + url)
    else:
      logging.error("failed to process master IP information" + str(client))

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
    self.mqtt_client.will_set("client/" + self.name, json.dumps({ "status" : "offline" }), 1, False)
    logging.debug("connecting to MQ " + self.mqtt.netloc)
    self.mqtt_client.connect(self.mqtt.hostname, self.mqtt.port)
    self.mqtt_client.loop_start()

  def on_connect(self, client, clientId, flags, rc):
    logging.debug("connected with result code " + str(rc))
    self.publish("client/" + self.name , json.dumps(self.on_connect_message()))

  def on_connect_message(self):
    repo = git.Repo(search_parent_directories=True)
    sha  = repo.head.object.hexsha
    return {
      "status" : "online",
      "git"    : repo.git.rev_parse(sha, short=4)
    }
  
  def on_message(self, client, clientId, msg):
    topic = msg.topic
    msg   = str(msg.payload.decode("utf-8"))
    logging.debug("received message: " + topic + " : " + msg)
    self.handle_mqtt_message(topic, msg)

  def handle_mqtt_message(self, topic, msg):
    pass

  def follow(self, topic):
    if self.mqtt_client is None: return
    logging.debug("following " + topic)
    self.mqtt_client.subscribe(topic)
    return self

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
