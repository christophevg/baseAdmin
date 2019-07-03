import logging
logger = logging.getLogger(__name__)

import os

from baseadmin.endpoint import me, command

def run(script, *args):
  script = os.path.join(os.path.dirname(__file__), script)
  os.system("{0} {1}".format(script, " ".join(args)))

@command("screen")
def on_screen(args):
  logger.warn("updating screen settings: {0}".format(args))
  reboot = False

  current = me.state

  if "orientation" in args and args["orientation"] and args["orientation"] != "":
    reboot = True
    current["orientation"] = args["orientation"]
    run("update-screen-orientation.sh", args["orientation"])

  if "hdmi" in args and "group" in args["hdmi"] and "mode" in args["hdmi"]:
    if args["hdmi"]["group"] != "" and args["hdmi"]["mode"] != "":
      reboot = True
      current["hdmi"] = args["hdmi"]
      run("update-screen-hdmi.sh", args["hdmi"]["group"], args["hdmi"]["mode"])

  me.state = current

  if reboot:
    logger.warn("rebooting due to screen update")
    os.system("( sleep 10; sudo reboot) &")
    return "rebooting due to screen update..."
