import logging
import time

from servicefactory import Service

from local import HOSTNAME

import local.config
import local.logging

import remote.client

@Service.API.endpoint(port=1234)
class Client(Service.base, remote.client.base):

  def handle_mqtt_message(self, topic, msg):
    logging.info(topic + " : " + msg)

  def loop(self):
    logging.info("looping...")
    time.sleep(5)

  def finalize(self):
    logging.info("finalising...")

  @Service.API.handle("action")
  def handle_action(self, data):
    logging.info("handling action...")
    logging.info(data)

if __name__ == "__main__":
  Client("DemoClient").follow("#").run()
