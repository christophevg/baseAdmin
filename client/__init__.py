# change logging formatter

import logging

formatter = logging.Formatter(
  "%(asctime)s [%(levelname)-5.5s] %(message)s"
)
logger = logging.getLogger()

logger.setLevel(logging.DEBUG) # TODO make this configurable

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

# ensure we have local environment in scope, also from dot env file

import os
import sys
from os.path import join, dirname, isfile
from dotenv import load_dotenv

script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
dotenv_path = join(script_path, "env.local")
if isfile(dotenv_path):
  logging.info("loading local environment configuration from " + dotenv_path)
  load_dotenv(dotenv_path)

LOGFILE = os.environ.get("LOGFILE")
if LOGFILE:
  if not os.path.exists(LOGFILE): touch(LOGFILE)
  fileHandler = logging.FileHandler(LOGFILE)
  fileHandler.setFormatter(formatter)
  logger.addHandler(fileHandler)

def disable_console_logging():
  logger.removeHandler(consoleHandler)

# silence loggers of some libs

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# The baseAdmin Client implements an end-point or node within the baseAdmin
# network as a service. It connects to the baseAdmin network and receives
# messages containing configuration updates. These updates are then dispatched
# to the corresponding services. A local cache of the configuration is
# maintained to allow for disconnected operation.

import time
import json

from servicefactory import Service

import backend.client
import client.config

@Service.API.endpoint(port=17171)
class Service(Service.base, backend.client.base):

  def __init__(self):
    super(self.__class__, self).__init__()
    self.parser.add_argument(
      "--config", type=str, help="configuration",
      default=os.environ.get("CONFIG_STORE")
    )

  def start(self):
    super(self.__class__, self).start()
    self.config  = client.config.Storable(
      "/opt/baseAdmin/config.json" if self.args.config is None else self.args.config
    )
    self.run()
  
  def subscribe(self):
    self.follow("client/" + self.name + "/config")
    # TODO refactor this
    self.handlers = {}

  def handle_mqtt_message(self, topic, msg):
    logging.info("received message: " + topic + " : " + msg)
    try:
      event = json.loads(msg)
      for handler in self.handlers[event["type"]]:
        logging.info("dispatching to " + handler)
        self.post(handler, event)
    except Exception as e:
      logging.error("event handling failed: " + repr(e))

  def loop(self):
    time.sleep(5)

  @Service.API.handle("register_message_handler")
  def handle_register_message_handler(self, data):
    args = json.loads(data)
    event       = args["event"]
    handler_url = args["handler"]
    logging.info("registering handler for " + event + " : " + handler_url)
    try:
      self.handlers[event].append(handler_url)
    except KeyError:
      self.handlers[event] = [ handler_url ]
