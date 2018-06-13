import os
import socket

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

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
IP = s.getsockname()[0]
s.close()

# change logging formatter

import logging

formatter = logging.Formatter(
  "%(asctime)s [%(levelname)-5.5s] %(message)s"
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

import backend.web
import backend.rest

import backend.resources
import backend.interface

from backend.plugins import *
