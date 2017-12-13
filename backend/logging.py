import os
import logging

formatter = logging.Formatter(
  "%(asctime)s [%(levelname)-5.5s] %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

LOGFILE = os.environ.get("LOGFILE")
if LOGFILE:
  if not os.path.exists(LOGFILE): touch(LOGFILE)
  fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName))
  fileHandler.setFormatter(logFormatter)
  logger.addHandler(fileHandler)

# silence loggers of some libs
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
