if __name__ == "__main__":
  import time
  import logging

  from servicefactory import Service

  import client

  @Service.API.endpoint(port=21212)
  class SomeService(Service.base):
    def __init__(self):
      r = client.Service.perform(
        "get_config",
        { "service" : "SomeService" }
      )
      self.config = r.json()
      logging.info("loaded config on boot: " + str(self.config))

    @Service.API.handle("config")
    def handle_config(self, data):
      logging.info("received config update : " + str(data))
    
    def loop(self):
      time.sleep(1000)

  SomeService().run()
