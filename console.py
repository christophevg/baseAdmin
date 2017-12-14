import logging
import backend.logging

import backend.config

from backend.client import Client

console = Client("console")
console.run()

try:
  logging.info("starting console event loop, interrupt with Ctrl+c")
  while True:
    pass
except KeyboardInterrupt:
  pass
