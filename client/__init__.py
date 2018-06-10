import os
import logging

LOG_FILE = os.environ.get("LOG_FILE")
if LOG_FILE:
  if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "a"):
      os.utime(LOG_FILE, None)
  fileHandler = logging.FileHandler(LOG_FILE)
  formatter = logging.Formatter(
    "%(asctime)s [%(levelname)-5.5s] %(message)s"
  )
  fileHandler.setFormatter(formatter)
  logger = logging.getLogger()
  logger.addHandler(fileHandler)

# silence loggers of some libs

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
