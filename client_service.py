if __name__ == "__main__":
  import time
  import logging

  from servicefactory import Service

  import client

  @Service.API.endpoint(port=21212)
  class SomeService(Service.base):
    def __init__(self):
      self.config = client.Service.get_config("SomeService")
      logging.info("loaded config on boot: " + str(self.config))

    @Service.API.handle("config")
    def handle_config(self, data):
      logging.info("received config update : " + str(data))

    @Service.API.handle("action")
    def handle_action(self, data):
      logging.info("received action command : " + str(data))
    
    def loop(self):
      time.sleep(1000)

  SomeService().run()
