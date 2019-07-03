import logging
logger = logging.getLogger(__name__)

import os

from baseadmin.endpoint import command

@command("reboot")
def on_reboot(args):
  logger.warn("rebooting...")
  os.system("( sleep 10; sudo reboot ) &")

@command("shutdown")
def on_shutdown(args):
  logger.warn("shutting down...")
  os.system("( sleep 10; sudo shutdown ) &")

@command("update")
def on_update(args):
  fname = os.path.expanduser("~/update_baseadmin_app")
  with open(fname, "a"):
    os.utime(fname, None)
  os.system("( sleep 10; sudo reboot ) &")

