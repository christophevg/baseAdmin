import logging
logger = logging.getLogger(__name__)

import os

from baseadmin.endpoint import me, command

from . import generate_wpa_supplicant

@command("addNetwork")
def on_add_network(args):
  if not "ssid" in args or not "psk" in args or args["ssid"] == "" or args["psk"] == "":
    raise KeyError("invalid network arguments")
  
  current = me.state
  
  if not "networks" in current: current["networks"] = {}
  current["networks"][args["ssid"]] = args["psk"]
  
  generate_wpa_supplicant(current["networks"])
  
  me.state = current

@command("removeNetwork")
def on_remove_network(args):
  if not "ssid" in args or args["ssid"] == "":
    raise KeyError("invalid network arguments")

  current = me.state
  
  if not "networks" in current: current["networks"] = {}
  try: 
    del current["networks"][args["ssid"]]
    generate_wpa_supplicant(current["networks"])
  except KeyError:
    logger.warn("unknown SSID:  {0}".format(args["ssid"]))

  me.state = current
