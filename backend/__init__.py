import os
import socket

BACKEND_MODE = os.environ.get("BACKEND_MODE")
if not BACKEND_MODE:
  BACKEND_MODE = "cloud"

CLOUD  = BACKEND_MODE == "cloud"
MASTER = BACKEND_MODE == "master"

APP_NAME = os.environ.get("APP_NAME")
if not APP_NAME:
  APP_NAME = "baseAdmin"

APP_AUTHOR = os.environ.get("APP_AUTHOR")
if not APP_AUTHOR:
  APP_AUTHOR = "Christophe VG"

APP_DESCRIPTION = os.environ.get("APP_DESCRIPTION")
if not APP_DESCRIPTION:
  APP_DESCRIPTION = "A baseAdmin Demo"

HOSTNAME = socket.gethostname()  

# change logging formatter

import logging

formatter = logging.Formatter(
  '%(asctime)s - %(name)-10.10s - [%(levelname)-5.5s] - %(message)s'
)
logger = logging.getLogger()

LOG_LEVEL = os.environ.get("LOG_LEVEL")
if not LOG_LEVEL:
  LOG_LEVEL = "DEBUG"
logger.setLevel(logging.getLevelName(LOG_LEVEL))

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

def disable_console_logging():
  logger.removeHandler(consoleHandler)

logging.getLogger("git.cmd").setLevel(logging.WARNING)

import backend.web
import backend.rest

import backend.interface

if MASTER:
  import backend.resources.master
  logging.info("Running Backend in MASTER mode")
  from backend.plugins import *
else:
  import backend.resources.cloud
  logging.info("Running Backend in CLOUD mode")
