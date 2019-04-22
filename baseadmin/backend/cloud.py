import os
import logging
import requests

import socket
import time

from servicefactory import Service

from backend import HOSTNAME

INTERVAL = os.environ.get("IP_CHECK_INTERVAL")
if not INTERVAL:
  INTERVAL = 60
else:
  INTERVAL = int(INTERVAL)

CLOUD_URL = os.environ.get("CLOUD_URL")
if not CLOUD_URL:
  CLOUD_URL = "http://admin:admin@localhost:5001/api"

class Connector(Service.base):
  def __init__(self):
    logging.info("cloud connector starting...")
    self.previous_ip = None
    self.current_ip  = None

  def refresh_current_ip(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
      s.connect(("8.8.8.8", 80))
      self.previous_ip = self.current_ip
      self.current_ip  = s.getsockname()[0]
    except Exception as e:
      logging.warn("unable to refresh current ip address" + str(e))
    finally:
      s.close()

  def loop(self):
    self.refresh_current_ip()
    if self.current_ip != self.previous_ip: self.post_current_ip()
    time.sleep(INTERVAL)

  def post_current_ip(self):
    logging.info("posting update of IP address: " + self.current_ip)
    data = {
      "ip" : self.current_ip
    }
    try:
      result = requests.post(
        os.path.join(CLOUD_URL, "master", HOSTNAME),
        json=data
      )
    except Exception as e:
      logging.warn("unable to post update of IP address: " + str(e))
      self.current_ip = self.previous_ip

if __name__ == "__main__":
  Connector().run()
