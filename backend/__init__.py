import os
import socket

APP_NAME = os.environ.get("APP_NAME")
if not APP_NAME:
  APP_NAME = "baseAdmin"

HOSTNAME = socket.gethostname()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
IP = s.getsockname()[0]
s.close()

# ensure we have local environment in scope, also from dot env file

import logging

import sys
from os.path import join, dirname, isfile
from dotenv import load_dotenv

script_path = os.getcwd()
dotenv_path = join(script_path, "env.local")
if isfile(dotenv_path):
  logging.info("loading local environment configuration from " + dotenv_path)
  load_dotenv(dotenv_path)


import backend.web
import backend.rest

import backend.resources
import backend.interface
