if __name__ == "__main__":
  import time
  from servicefactory import Service
  import backend.client

  @Service.API.endpoint(port=21212)
  class SomeService(Service.base):
    def __init__(self):
      backend.client.Service.perform(
        "register_message_handler",
        {
          "event"   : "event",
          "handler" : self.url("action")
        }
      )
      
    @Service.API.handle("action")
    def handle_action(self, data):
      print("received message through backend client")
      print(str(data))
    
    def loop(self):
      time.sleep(1000)

  SomeService().run()
