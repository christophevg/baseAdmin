import logging
import time
import json
import socket
from uuid import UUID
from base64 import b64encode, b64decode

import mongomock

from baseadmin import pki, private_key, public_key
from baseadmin.messaging import MessageQueue, Outbox

def create_mq(timeout=5000):
  outbox = Outbox(mongomock.MongoClient().db, timeout=timeout)
  client = MQClientMock()
  mq     = MessageQueue(client=client, outbox=outbox)
  return (mq, client, outbox)

def test_send_single_message_without_ack():
  (mq, client, outbox) = create_mq()
  topic   = "testing/sending"
  payload = { "hello" : "world" }
  mq.publish(topic, payload)
  time.sleep(0.5) # give MQ time to process outbox
  assert len(client.queue) == 1
  item = client.queue[0]
  assert item[0] == topic
  assert item[2] == 1
  assert item[3] == False
  message = json.loads(item[1])
  assert message["payload"] == payload
  UUID(message["header"]["id"], version=4)
  name = socket.gethostname()
  assert message["header"]["origin"] == name
  assert message["header"]["topic"] == topic
  expected_message = {
    "header" : {
      "id"    : message["header"]["id"],
      "topic" : topic,
      "origin": name
    },
    "payload" : payload
  }
  encoded = b64encode(json.dumps(expected_message, sort_keys=True))
  assert encoded == message["security"]["encoded"]
  pki.validate(encoded, b64decode(message["security"]["signature"]), public_key)

def test_single_message_delivery_without_ack():
  (mq, client, outbox) = create_mq()
  delivery = []
  def accept(mq, topic, message):
    delivery.append({ "topic": topic, "message": message })
  mq.on("testing/delivery", accept)
  mq.publish("testing/delivery", { "hello" : "delivery" })
  time.sleep(0.2) # give MQ time to process outbox
  client.deliver()
  assert len(delivery) == 1
  assert delivery[0]["topic"] == "testing/delivery"
  assert delivery[0]["message"]["payload"] == {"hello": "delivery"}

def test_single_message_with_ack_resending():
  (mq, client, outbox) = create_mq(timeout=500)
  delivery = []
  def accept(mq, topic, message):
    delivery.append({ "topic": topic, "message": message })
  mq.on("testing/delivery", accept)
  mq.publish("testing/delivery", { "hello" : "delivery" }, ack=True)
  time.sleep(0.2) # give MQ time to process outbox
  client.deliver()
  assert len(delivery) == 1
  time.sleep(0.3) # wait for timeout
  client.deliver()
  assert len(delivery) == 2
  # client.publish()
  
'''
    MQClientMock is a minimalistic mock of a MQTT (Paho) client.
'''

class MQClientMock(object):
  on_connect    = None
  on_subscribe  = None
  on_message    = None
  on_disconnect = None
  
  def __init__(self):
    self.username     = None
    self.password     = None
    self.will_topic   = None
    self.will_payload = None
    self.will_qos     = 0
    self.will_reain   = False
    self.hostname     = None
    self.port         = None
    self.handlers     = {}
    self.queue        = []

  def username_pw_set(self, username, password):
    self.username = username
    self.password = password

  def will_set(self, topic, payload=None, qos=0, retain=False):
    self.will_topic   = topic
    self.will_payload = payload
    self.will_qos     = qos
    self.will_reatin  = retain

  def connect(self, hostname, port):
    self.hostname = hostname
    self.port     = port

  def loop_start(self):
    pass

  def message_callback_add(self, topic, handler):
    self.handlers[topic] = handler

  def subscribe(self, topic):
    return (0, 0)

  def publish(self, topic, payload, qos=0, retain=False):
    self.queue.append((topic, payload, qos, retain))

  def disconnect(self):
    pass

  def deliver(self):
    try:
      for item in self.queue:
        logging.debug("delivering {0}".format(item))
        self.handlers[item[0]](self, None, MessageMock(item[0], item[1]))
    except Exception as e:
      logging.error(e)

class MessageMock(object):
  def __init__(self, topic, payload):
    self.topic   = topic
    self.payload = payload
