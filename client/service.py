import time
import logging

from servicefactory import Service

import client.service

class base(Service.base):
  def __init__(self):
    self.config = client.Service.get_config(self.__class__.__name__)
    logging.info("loaded config on boot: " + str(self.config))

  @Service.API.handle("__config")
  def __handle_config(self, data):
    logging.info("received config update : " + str(data))

  @Service.API.handle("__heartbeat")
  def __handle_heartbeat(self, data):
    pass
    
  def loop(self):
    time.sleep(1000)

# passthrough Service API support (cosmetic)
class API(Service.API):
  pass