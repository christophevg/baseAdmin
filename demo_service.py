import logging

import client.service
from client.service import API

@API.endpoint(port=21212)
class SomeService(client.service.base):

  @API.handle("action")
  def handle_action(self, data):
    logging.info("received action command : " + str(data))

if __name__ == "__main__":
  SomeService().run()
