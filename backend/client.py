import backend
from backend import HOSTNAME, IP

class Client():
  def __init__(self, name="client"):
    self.name = name

  def run(self):
    backend.mq.connect(self.name)
