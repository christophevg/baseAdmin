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

  def process_arguments(self):
    super(self.__class__, self).process_arguments()
    self.config  = client.config.Storable(
      "./config.json" if self.args.config is None else self.args.config
    )
    # TODO push current config to all services (just to make sure ;-))

  def start(self):
    super(self.__class__, self).start()
    # also start this service
    self.run()
  
  def subscribe(self):
    self.follow("client/" + self.name + "/services")
    current = self.config.current()
    if "services" in current:
      for service_name in current["services"]:
        self.follow("client/" + self.name + "/service/" + service_name)

  def handle_mqtt_message(self, topic, msg):
    logging.info("received message: " + topic + " : " + msg)
    try:
      parts  = topic.split("/")
      scope  = parts[2]
      update = json.loads(msg)
      if len(parts) > 3:
        service = parts[3]
        self.handle_service_update(service, update)
      else:
        self.handle_services_update(update)
    except Exception as e:
      logging.error("message handling failed: " + repr(e))
  
  def handle_services_update(self, update):
    current = self.config.current()
    if not "services" in current:
      current["services"] = {}
    try:
      current["ts"] = update["ts"]
    except KeyError:
      current["ts"] = time.time()

    if "location" in update:
      current["services"][update["service"]] = {
        "location" : update["location"]
      }
    else:
      current["services"].pop(update["service"], None)
    self.config.update(current)
    self.subscribe()
  
  def handle_service_update(self, service, update):
    current = self.config.current()
    try:
      current["ts"] = update["ts"]
    except KeyError:
      current["ts"] = time.time()
    if not "config" in current["services"][service]:
      current["services"][service]["config"] = {}
    for k in update["config"]:
      current["services"][service]["config"][k] = update["config"][k]
    self.config.update(current)
    # push config to service
    self.post(
      current["services"][service]["location"],
      current["services"][service]["config"]      
    )

  def loop(self):
    time.sleep(5)
    # TODO handle scheduled updates

  @Service.API.handle("get_config")
  def get_config(self, data=None):
    try:
      args    = json.loads(data)
      service = args["service"]
      config  = self.config.current()["services"][service]["config"]
      logging.debug("providing config for " + service + " : " + str(config))
      return json.dumps(config)
    except Exception as e:
      logging.error("failed to provide configuration : " + str(e))
      return json.dumps(None)
