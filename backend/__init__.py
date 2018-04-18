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

import common.logging

import backend.data

import backend.mq

import backend.web
import backend.rest

import backend.resources
import backend.interface
