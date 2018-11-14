import os

import logging

from flask import Flask
import jinja2

server = Flask(__name__)

my_loader = jinja2.ChoiceLoader([
  jinja2.FileSystemLoader("baseadmin/backend/templates/"),
  server.jinja_loader,
])
server.jinja_loader = my_loader

import baseadmin.backend.rest
import baseadmin.backend.interface
import baseadmin.backend.resources
