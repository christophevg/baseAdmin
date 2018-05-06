if __name__ == "__main__":
  import time
  import logging

  from servicefactory import Service

  import client

  @Service.API.endpoint(port=21212)
  class SomeService(Service.base):
    def __init__(self):
      client.Service.perform(
        "register_message_handler",
        {
          "event"   : "event",
          "handler" : self.url("action")
        }
      )
      
    @Service.API.handle("action")
    def handle_action(self, data):
      logging.info("received message through backend client")
      logging.info(str(data))
    
    def loop(self):
      time.sleep(1000)

  SomeService().run()
