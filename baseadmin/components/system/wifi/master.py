import logging
logger = logging.getLogger(__name__)

import os

from baseadmin.backend.interface import register_component
from baseadmin.backend.socketio  import command, register_state_provider

from . import repository, generate_wpa_supplicant

# add component UI

register_component("Wifi.js", os.path.dirname(__file__))

# provide our own master wifi networks

register_state_provider("networks", repository.getNames)

# respond to system actions

@command("addNetwork")
def on_add_network(args):
  logger.debug(args)
  if not "ssid" in args or not "psk" in args or args["ssid"] == "" or args["psk"] == "":
    raise KeyError("invalid network arguments")
  
  repository.add(args["ssid"], args["psk"])
  generate_wpa_supplicant(repository.getMap())

@command("removeNetwork")
def on_remove_network(args):
  logger.debug(args)
  if not "ssid" in args or args["ssid"] == "":
    raise KeyError("invalid network arguments")

  repository.remove(args["ssid"])
  generate_wpa_supplicant(repository.getMap())
