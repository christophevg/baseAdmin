import logging
import time

import baseadmin
baseadmin.init()

from baseadmin.messaging import MessageQueue, MQError

def a(mq, topic, msg):
  logging.info("received by a: {0} : {1}".format(topic, str(msg)))
  mq.publish("testing/acks", {"info" : "ok 1"}, ack=True)
  mq.publish("testing/acks", {"info" : "ok 2"}, ack=True)
  mq.publish("testing/acks", {"info" : "ok 3"}, ack=True)

def b(mq, topic, msg):
  logging.info("received by b: {0} : {1}".format(topic, str(msg)))
  return { "b" : "ok" }

def on_connect(mq):
  logging.info("subscribing...")
  mq.on("a", a)
  mq.on("b", b)

mq = MessageQueue(
  on_connect=on_connect,
  last_will={"topic": "exit", "message": "gone"}
)

try:
  mq.connect()
  while(True):
    time.sleep(0.1)
except MQError as e:
  logging.error("could not connect to mq broker: {0}".format(str(e)))
except KeyboardInterrupt:
  mq.disconnect()
