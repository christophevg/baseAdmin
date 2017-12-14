import sys
import argparse
import requests
import logging

import backend
import backend.logging

class Client():
  def __init__(self, name="client", description=None):
    self.name = name
    if description is None:
      description = self.name + ": a baseAdmin client."

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--backend",  type=str, help="backend url.",      default=None)
    parser.add_argument("--username", type=str, help="backend user.",     default=None)
    parser.add_argument("--password", type=str, help="backend password.", default=None)

    args = parser.parse_args()

    self.backend  = args.backend
    self.username = args.username
    self.password = args.password
    self.mq       = None

  def run(self):
    if not self.get_mq_connection_details(): return False
    backend.mq.connect(self.name, mq=self.mq)
    return True
    
  def get_mq_connection_details(self):
    if not self.backend: return True

    logging.info("requesting MQ connection details from " + self.backend)
    response = requests.get(
      self.backend + "/api/mq/connection/mqtt",
      auth=(self.username, self.password)
    )

    if response.status_code != requests.codes.ok:
      logging.error("request for MQ connection details failed: " + str(response.status_code))
      return False

    self.mq = response.json()
    return True
