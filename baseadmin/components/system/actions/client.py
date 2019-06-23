import logging
logger = logging.getLogger(__name__)

import os

from baseadmin.endpoint import command

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
  raise NotImplementedError("updating is not yet implemented...")
  # os.system("update.sh")
