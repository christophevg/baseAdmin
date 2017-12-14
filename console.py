import logging
import time

import backend.logging
import backend.config

from backend.client import Client

def event_loop():
  logging.info("starting console event loop, interrupt with Ctrl+c")
  try:
    while True:
      time.sleep(10)
  except KeyboardInterrupt:
    pass

console = Client("console")
if console.run(): event_loop()
