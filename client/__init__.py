import os
import logging

LOG_FILE = os.environ.get("LOG_FILE")
if LOG_FILE:
  if not os.path.exists(LOG_FILE): touch(LOG_FILE)
  fileHandler = logging.FileHandler(LOG_FILE)
  fileHandler.setFormatter(formatter)
  logger.addHandler(fileHandler)

# silence loggers of some libs

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
