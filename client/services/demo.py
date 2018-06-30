import logging
import json
import time

import client.service
from client.service import API

@API.endpoint(port=21212)
class DemoService(client.service.base):

  def loop(self):
     logging.info(client.endpoint.API.get_master())
     time.sleep(3)

  @API.handle("action")
  def handle_action(self, data):
    data = json.loads(data)
    logging.info("received action command : " + str(data))
    self.publish("info", data)

if __name__ == "__main__":
  DemoService().run()
