import logging
logger = logging.getLogger(__name__)

import os
import shutil

def run(script, *args):
  script = os.path.join(os.path.dirname(__file__), script)
  os.system("sudo {0} {1}".format(script, " ".join(args)))

def generate_wpa_supplicant(wifi):
  try:
    # make a copy of the initial file as a base for all  updates
    # this also always keeps the initial/mother network
    if not os.path.exists("/etc/wpa_supplicant/wpa_supplicant.conf.org"):
      shutil.os.system('sudo cp "{}" "{}"'.format(
        "/etc/wpa_supplicant/wpa_supplicant.conf",
        "/etc/wpa_supplicant/wpa_supplicant.conf.org"
      ))

    # start with fresh/original file and add all wifi entries
    shutil.os.system('sudo cp "{}" "{}"'.format(
      "/etc/wpa_supplicant/wpa_supplicant.conf.org",
      "/etc/wpa_supplicant/wpa_supplicant.conf"
    ))
    for ssid, psk in wifi.items():
      run("add-wifi.sh", ssid, psk, ssid)
  except FileNotFoundError:
    logger.error("file not found...")
