import logging
logger = logging.getLogger(__name__)

import os

from baseadmin.backend.interface import register_component
from baseadmin.backend.socketio  import command

# add component UI

register_component("SystemActions.js", os.path.dirname(__file__))

# respond to system actions

@command("reboot")
def on_reboot(args):
  logger.warn("rebooting...")
  os.system("sudo reboot")

@command("shutdown")
def on_shutdown(args):
  logger.warn("shutting down...")
  os.system("sudo shutdown")

@command("update")
def on_update(args):
  logger.warn("TODO updating...")
  fname = os.path.expanduser("~/update_baseadmin_app")
  with open(fname, "a"):
    os.utime(fname, None)
  os.system("sudo reboot")
