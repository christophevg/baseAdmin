import time
import random
import logging

class VariableSleep(object):
  def __init__(self, base, variable):
    self.base     = base
    self.variable = variable

  def __str__(self):
    return "{0}~{1}s".format(self.base, self.variable)
  
  def sleep(self):
    interval = self.base + random.randint(1, self.variable)
    logging.debug("sleeping for {0}s".format(interval))
    time.sleep(interval)
