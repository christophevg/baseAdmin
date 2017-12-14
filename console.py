import logging
import time

import backend.logging
import backend.config

from backend.client import Client
from backend.mq     import follow

def event_loop():
  logging.info("starting console event loop, interrupt with Ctrl+c")
  try:
    while True:
      time.sleep(10)
  except KeyboardInterrupt:
    pass

def print_msg(msg):
  print(msg)

console = Client("console")
if console.run():
  follow("#", print_msg)
  event_loop()
