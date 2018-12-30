import time
import logging
import json

from servicefactory import Service

import client.endpoint

class base(Service.base):
  def __init__(self):
    self.config = client.endpoint.API.get_config(self.__class__.__name__)
    logging.info("loaded config on boot: " + str(self.config))
    self.on_config_update()

  @Service.API.handle("__config")
  def __handle_config(self, data):
    data = data.decode('UTF-8')
    if data is None or data == "":
      self.config = None
    else:
      self.config = json.loads(data)
    logging.info("received config update : " + str(self.config))
    self.on_config_update()

  def on_config_update(self):
    pass

  @Service.API.handle("__heartbeat")
  def __handle_heartbeat(self, data):
    pass

  def publish(self, message, data):
    client.endpoint.API.publish_service_event(self.__class__.__name__, message, data)

  def loop(self):
    time.sleep(1000)

# passthrough Service API support (cosmetic)
class API(Service.API):
  pass