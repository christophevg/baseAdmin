import logging
import json
import time
import uuid

millis = lambda: int(round(time.time() * 1000))

import pymongo

from threading import Thread

try:
  from urllib.parse import urlparse
except ImportError:
  from urlparse import urlparse

import paho.mqtt.client as mqtt

from base64 import b64encode, b64decode

from baseadmin import HOSTNAME, get_db, pki, private_key, public_key

class MQError(Exception):
  pass

'''
    A MessageQueue is an endpoint of an MQTT network, providing persistence of
    messages, retrying as part of acknowledgement management, signing and
    integrity validation.
'''

class MessageQueue(object):
  def __init__(self, on_connect=None, on_message=None,
                     url="mqtt://localhost:1883",
                     id=HOSTNAME, last_will=None,
                     client=None, outbox=None):
    self.id = id
    self.client = client or mqtt.Client()
    self.client.on_connect    = self.on_connect
    self.client.on_subscribe  = self.on_subscribe
    self.client.on_message    = self.on_message
    self.client.on_disconnect = self.on_disconnect

    self.on_connect_handler = on_connect
    self.on_message_handler = on_message

    self.config = urlparse(url)
    if self.config.username and self.config.password:
      self.client.username_pw_set(self.config.username, self.config.password)

    if last_will:
      self.client.will_set(last_will["topic"], last_will["message"], 1, False)

    self.outbox = outbox or Outbox()

    self.processor = Thread(target=self.process_outbox)
    self.processor.daemon = True
    self.processor.start()

  def connect(self):
    logging.debug("connecting to {0} as {1}".format(
      self.config.netloc, self.id)
    )
    try:
      self.client.connect(self.config.hostname, self.config.port)
      self.client.loop_start()
    except Exception as e:
      raise MQError(str(e))

  def on_connect(self, client, id, flags, rc):
    logging.debug("connected with result code {0} as {1}".format(
      str(rc), id
    ))
    if rc == 0:
      ack_topic = "{0}/ack".format(self.id)
      self.client.message_callback_add(ack_topic, self.on_ack)
      self.client.subscribe(ack_topic)
      if self.on_connect_handler:
        self.on_connect_handler(self)

  def on(self, topic, callback):
    def wrapper(client, id, msg):
      topic = msg.topic
      try:
        msg = json.loads(str(msg.payload.decode("utf-8")))
        result = callback(self, topic, msg)
        if "ack" in msg and "id" in msg:
          message = json.dumps({ "id" : msg["id"], "result" : result })
          self.client.publish(msg["ack"], message,  1, False)
          logging.debug("acknowledged {0} ".format(msg["id"]))
      except ValueError as e:
        logging.error("failed to load message content: {0}".format(str(e)))
      except Exception as e:
        logging.error("failed to handle message: {0}".format(str(e)))
        
    self.client.message_callback_add(topic, wrapper)
    (result, mid) = self.client.subscribe(topic)
    logging.debug("requested subscription to {0} with mid={1}".format(
      topic, mid
    ))

  def on_subscribe(self, client, id, mid, granted_qos):
    logging.debug("subscription confirmed for mid={0}".format(mid))

  def on_message(self, client, id, msg):
    (topic, msg) = self.parse(msg)
    logging.info("received unexpected message: {0} : {1}".format(
      topic, msg
    ))
    if self.on_message_handler:
      self.on_message_handler(topic, msg)

  def on_ack(self, client, id, msg):
    (_, msg) = self.parse(msg)
    logging.debug("received acknowledgement for {0}".format(msg["id"]))
    self.outbox.ack(msg["id"])

  def parse(self, msg):
    return (msg.topic, json.loads(str(msg.payload.decode("utf-8"))))

  def publish(self, topic, data, ack=False):
    self.outbox.add(topic, data, ack)
    logging.debug("queued message ({0})".format(str(self.outbox.size())))

  def process_outbox(self):
    while True:
      for item in self.outbox:
        try:
          self.client.publish(item["topic"], self.construct_message(item),  1)
          self.outbox.sent(item["id"])
          logging.debug("sent message to {0} : {1}".format(
            item["topic"], item["msg"]
          ))
        except Exception as e:
          logging.error("failed to send msg: {0}".format(str(e)))
          # TODO this will loop until it doesn't fail, how to handle?
      time.sleep(0.1)

  def construct_message(self, item):
    message = {
      "header" : {
        "id"    : item["id"],
        "topic" : item["topic"],
        "origin": self.id
      },
      "payload" : item["msg"]
    }
    if item["ack"]:
      message["header"]["ack"] = "{0}/ack".format(self.id)
    message["security"] = self.sign(message)
    return json.dumps(message)

  def sign(self, payload):
    encoded   = b64encode(json.dumps(payload, sort_keys=True))
    signature = b64encode(pki.sign(encoded, private_key))
    return {
      "encoded"   : encoded,
      "signature" : signature
    }

  def validate(self, payload):
    pass
    #  TODO

  def disconnect(self):
    logging.debug("disconnecting from {0}".format(self.config.netloc))
    self.client.disconnect()

  def on_disconnect(self, client, id, rc):
    logging.warn("message broker disconnected")

'''
    An Outbox manages items that need to be send, providing an iterable
    interface to these messages. It transparently persists the items to a db.
    Items can require acknowledgement within a (optionally) given timeout.
    After this timeout has been reached, the items are offered again as items
    that need to be send. Order of the messages is respected. Every message is
    given a UUID.
'''
class Outbox(object):
  def __init__(self, db=None, timeout=5000):
    self.db = db or get_db()
    self.timeout = timeout
    self.messages = {}
    self.last = 0
    self.load()
  
  def load(self):
    for item in self.db.outbox.find():
      self.messages[item["_id"]] = item
    logging.debug("loaded {0} outbox items".format(len(self.messages)))

  def __iter__(self):
    return self

  def messages_to_send(self):
    return sorted(
      [m for m in self.messages.values() if millis()-m["last"] > self.timeout],
      key = lambda x: x["last"]
    )

  # python 2.x support
  def next(self):
    return self.__next__()

  def __next__(self):
    try:
      return self.messages_to_send()[0]
    except IndexError:
      raise StopIteration

  def size(self, all=False):
    return len(self.messages_to_send()) if not all else len(self.messages)

  def add(self, topic, msg, ack=False):
    id = str(uuid.uuid4())
    last = millis() - self.timeout*2 # ensure it will surely be addressed
    if last <= self.last:            # ensure no duplicate last timestamps
      last = self.last + 1           # respect order
    self.last = last
    item = {
      "id"    : id,
      "topic" : topic,
      "msg"   : msg,
      "ack"   : ack,
      "last"  : self.last
    }
    self.db.outbox.insert_one(item)
    self.messages[id] = item
    logging.debug("added outbox item: {0}".format(str(item)))
    return id

  def sent(self, id):
    try:
      if self.messages[id]["ack"]:
        last = millis()
        self.messages[id]["last"] = last
        self.db.outbox.update_one({"id" : id}, {"$set" : {"last": last}} )
        logging.debug("waiting for acknowledgement of {0}".format(id))
      else:
        del self.messages[id]
        self.db.outbox.delete_one({"id": id})
        logging.debug("removed {0}".format(id))
    except KeyError:
      logging.warn("unknow item id: {0}".format(id))

  def ack(self, id):
    try:
      del self.messages[id]
      self.db.outbox.delete_one({"id": id})
    except KeyError:
      logging.warn("unknow item id: {0}".format(id))
