import time
import random

class VariableSleep(object):
  def __init__(self, base, variable):
    self.base        = base
    self.variable    = variable
    self.generate_next_interval()

  def generate_next_interval(self):
    self.interval = self.base + random.randint(1, self.variable)

  def __str__(self):
    return "{0}~{1}={2}s".format(self.base, self.variable, self.interval)
  
  def sleep(self):
    time.sleep(self.interval)
    self.generate_next_interval()
