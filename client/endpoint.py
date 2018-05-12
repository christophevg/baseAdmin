# The baseAdmin Client implements an end-point or node within the baseAdmin
# network as a service. It connects to the baseAdmin network and receives
# messages containing configuration updates. These updates are then dispatched
# to the corresponding services. A local cache of the configuration is
# maintained to allow for disconnected operation.

import os
import logging
import time
import json
import requests

from servicefactory import Service

import backend.client
import client.config

@Service.API.endpoint(port=17171)
class Runner(Service.base, backend.client.base):

  def __init__(self):
    super(self.__class__, self).__init__()
    self.parser.add_argument(
      "--config", type=str, help="configuration",
      default=os.environ.get("CONFIG_STORE")
    )
    self.last_service_check = time.time()

  def process_arguments(self):
    super(self.__class__, self).process_arguments()
    self.config  = client.config.Storable(
      "./config.pkl" if self.args.config is None else self.args.config,
      on_group_join     = self.join_group,
      on_group_leave    = self.leave_group,
      on_service_add    = self.add_service,
      on_service_remove = self.remove_service,
      on_service_update = self.push_configuration_update,
      on_service_action = self.perform_action
    )

  def start(self):
    super(self.__class__, self).start()
    for service in self.config.list_services():
      self.push_configuration_update(service)
    # also start this service
    self.run()

  def loop(self):
    self.config.handle_scheduled()
    self.check_services()
    time.sleep(0.05)
  
  def on_connect(self, client, clientId, flags, rc):
    super(self.__class__, self).on_connect(client, clientId, flags, rc)
    self.follow("client/" + self.name + "/services")
    self.follow("client/all/services")
    self.publish("client/" + self.name + "/status", {
      "last-message" : self.config.get_last_message_id()
    })
    groups = self.config.list_groups()
    for group in groups:
      self.follow("client/" + group + "/services")
    for service in self.config.list_services():
      self.follow("client/" + self.name + "/service/" + service)
      self.follow("group/all/service/" + service)
      for group in groups:
        self.follow("group/" + group + "/service/" + service)

  def join_group(self, group):
    self.follow("group/" + group + "/services")
    for service in self.config.list_services():
      self.follow("group/" + group + "/service/" + service)
  
  def leave_group(self, group):
    self.unfollow("group/" + group + "/services")
    for service in self.config.list_services():
      self.unfollow("group/" + group + "/service/" + service)

  def add_service(self, service):
    self.follow("client/" + self.name + "/service/" + service)
    self.follow("group/all/service/" + service)
    for group in self.config.list_groups():
      self.follow("group/" + group + "/service/" + service)
  
  def remove_service(self, service):
    self.unfollow("client/" + self.name + "/service/" + service)
    self.unfollow("group/all/service/" + service)
    for group in self.config.list_groups():
      self.unfollow("group/" + group + "/service/" + service)

  def handle_mqtt_message(self, topic, msg):
    try:
      parts  = topic.split("/")
      scope  = parts[2]
      update = json.loads(msg)
      if len(parts) > 3:
        service = parts[3]
        self.config.update_service(service, update)
      else:
        self.config.update(update)
    except KeyError as e:
      self.fail("invalid message, missing property", e)
    except Exception as e:
      self.fail("message handling failed", e)

  def push_configuration_update(self, service):
    self.perform_action(
      service,
      {
        "command" : "__config",
        "payload" : self.config.get_service_configuration(service)
      }
    )

  def perform_action(self, service, action):
    try:
      self.post(
        self.config.get_service_location(service) + "/" + action["command"],
        action["payload"]
      )
    except requests.exceptions.ConnectionError as e:
      self.fail("could not connect to " + service, e)
    except Exception as e:
      self.fail("could not post to " + service + "/" + action, e)
    
  def publish(self, topic, message):
    super(self.__class__, self).publish(topic, json.dumps(message))

  def check_services(self):
    now = time.time()
    if now - self.last_service_check > 60:
      self.last_service_check = now
      for service in self.config.list_services():
        try:
          self.post(
            self.config.get_service_location(service) + "/__heartbeat",
            None
          )
        except Exception as e:
          self.fail("service is unavailable: " + service, e)

  @Service.API.handle("get_config")
  def handle_get_config(self, data=None):
    try:
      args    = json.loads(data)
      service = args["service"]
      config  = self.config.get_service_configuration(service)
      logging.debug("providing config for " + service + " : " + str(config))
      return json.dumps(config)
    except Exception as e:
      self.fail("failed to provide configuration", e)
      return json.dumps(None)

  @classmethod
  def get_config(cls, service):
    try:
      return cls.perform( "get_config", { "service" : service } ).json()
    except Exception as e:
      logging.error("failed to retrieve config for " + service + " : " + str(e))
      return None

# passthrough Service API support (cosmetic)
class API(Runner):
  pass
