import logging
import json

import client.service
from client.service import API

@API.endpoint(port=21212)
class SomeService(client.service.base):

  @API.handle("action")
  def handle_action(self, data):
    data = json.loads(data)
    logging.info("received action command : " + str(data))
    self.publish("info", data)

if __name__ == "__main__":
  SomeService().run()
