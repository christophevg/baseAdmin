import logging

from flask import Flask
import jinja2

server = Flask(__name__)

my_loader = jinja2.ChoiceLoader([
  jinja2.FileSystemLoader("backend/app/templates/"),
  server.jinja_loader,
])
server.jinja_loader = my_loader

import backend.rest
import backend.interface

from backend import MASTER

if MASTER:
  import backend.resources.master
  logging.info("Running Backend in MASTER mode")
  from backend.plugins.master import *
else:
  import backend.resources.cloud
  logging.info("Running Backend in CLOUD mode")
  from backend.plugins.cloud import *
