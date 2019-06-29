import logging
logger = logging.getLogger(__name__)

import os
from shutil import copyfile

def run(script, *args):
  script = os.path.join(os.path.dirname(__file__), script)
  os.system("{0} {1}".format(script, " ".join(args)))

def generate_wpa_supplicant(wifi):
  try:
    # make a copy of the initial file as a base for all  updates
    # this also always keeps the initial/mother network
    if not os.path.exists("/etc/wpa_supplicant/wpa_supplicant.conf.org"):
      copyfile(
        "/etc/wpa_supplicant/wpa_supplicant.conf",
        "/etc/wpa_supplicant/wpa_supplicant.conf.org"
      )

    # start with fresh/original file and add all wifi entries
    copyfile(
      "/etc/wpa_supplicant/wpa_supplicant.conf.org",
      "/etc/wpa_supplicant/wpa_supplicant.conf"
    )
    for ssid, psk in wifi.items():
      run("add-wifi.sh", ssid, pdk, ssid)
  except FileNotFoundError:
    logger.error("file not found...")
