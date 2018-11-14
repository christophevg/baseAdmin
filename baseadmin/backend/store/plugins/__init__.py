class Monitor(object):
  def __init__(self, store, runner):
    self.store = store
    self.mqtt  = runner

  def follows(self):
    return []

  def handle(self, topic, message):
    pass

from os.path import dirname, basename, isfile
import glob

modules = glob.glob(dirname(__file__)+"/*.py")

__all__ = [ basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
