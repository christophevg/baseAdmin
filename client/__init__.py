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
    self.current_subscriptions = []
    self.first_subscription = True

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
    if self.first_subscription:
      self.follow("client/" + self.name + "/services")
      self.first_subscription = False
    required   = self.config.list_services()
    deprecated = list(set(self.current_subscriptions) - set(required))
    additional = list(set(required) - set(self.current_subscriptions))
    for service in deprecated:
      self.unfollow("client/" + self.name + "/service/" + service)
    for service in additional:
      self.follow("client/" + self.name + "/service/" + service)
    self.current_subscriptions = required

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

  def handle_service_update(self, service, update):
    ts = None if not "ts" in update else update["ts"]
    self.config.update_service_configuration(service, update["config"], ts=ts)
    # push config to service
    try:
      self.post(
        self.config.get_service_location(service),
        self.config.get_service_configuration(service)      
      )
    except Exception as e:
      logging.warn("could not post update to " + service + " " + repr(e))

  def handle_services_update(self, update):
    ts = None if not "ts" in update else update["ts"]
    if "location" in update:
      self.config.add_service(update["service"], update["location"], ts=ts)
    else:
      self.config.remove_service(update["service"], ts=ts)
    self.subscribe()

  def loop(self):
    time.sleep(5)
    # TODO handle scheduled updates

  @Service.API.handle("get_config")
  def handle_get_config(self, data=None):
    try:
      args    = json.loads(data)
      service = args["service"]
      config  = self.config.get_service_configuration(service)
      logging.debug("providing config for " + service + " : " + str(config))
      return json.dumps(config)
    except Exception as e:
      logging.error("failed to provide configuration : " + str(e))
      return json.dumps(None)

  @classmethod
  def get_config(cls, service):
    try:
      return cls.perform( "get_config", { "service" : service } ).json()
    except Exception as e:
      logging.error("failed to retrieve config for " + service + " : " + str(e))
      return None
