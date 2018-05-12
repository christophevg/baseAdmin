# change logging formatter

import logging

formatter = logging.Formatter(
  "%(asctime)s [%(levelname)-5.5s] %(message)s"
)
logger = logging.getLogger()

logger.setLevel(logging.DEBUG) # TODO make this configurable

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

# ensure we have local environment in scope, also from dot env file

import os
import sys
from os.path import join, dirname, isfile
from dotenv import load_dotenv

script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
dotenv_path = join(script_path, "env.local")
if isfile(dotenv_path):
  logging.info("loading local environment configuration from " + dotenv_path)
  load_dotenv(dotenv_path)

LOGFILE = os.environ.get("LOGFILE")
if LOGFILE:
  if not os.path.exists(LOGFILE): touch(LOGFILE)
  fileHandler = logging.FileHandler(LOGFILE)
  fileHandler.setFormatter(formatter)
  logger.addHandler(fileHandler)

def disable_console_logging():
  logger.removeHandler(consoleHandler)

# silence loggers of some libs

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
