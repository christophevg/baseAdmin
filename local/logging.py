import os
import logging

def touch(fname, times=None):
  with open(fname, 'a'):
    os.utime(fname, times)

formatter = logging.Formatter(
  "%(asctime)s [%(levelname)-5.5s] %(message)s"
)
logger = logging.getLogger()

lhStdout = None
if len(logger.handlers) > 0:
  lhStdout = logger.handlers[0]  # stdout is the only handler initially

logger.setLevel(logging.DEBUG)

# TODO make this configurable, e.g. not for curses clients
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

LOGFILE = os.environ.get("LOGFILE")
if LOGFILE:
  if not os.path.exists(LOGFILE): touch(LOGFILE)
  fileHandler = logging.FileHandler(LOGFILE)
  fileHandler.setFormatter(formatter)
  logger.addHandler(fileHandler)
  if lhStdout:
    # remove default stdout handler
    logger.removeHandler(lhStdout)

# silence loggers of some libs
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
