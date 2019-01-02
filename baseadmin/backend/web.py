import os
import logging

from flask import Flask
import jinja2

import baseadmin

reason = None

def server(environ, start_response):
  global reason
  data = "baseAdmin could not be initialized: {0}\n".format(reason)
  status = '200 OK'
  response_headers = [
    ('Content-type', 'text/plain'),
    ('Content-Length', str(len(data)))
  ]
  start_response(status, response_headers)
  return iter([data])

try:
  server = Flask(__name__)

  my_loader = jinja2.ChoiceLoader([
    jinja2.FileSystemLoader("baseadmin/backend/templates/"),
    server.jinja_loader,
  ])
  server.jinja_loader = my_loader

  # baseadmin.backend.init()
  # import baseadmin.backend.rest
  # import baseadmin.backend.interface

  logging.info("baseAdmin backend web server is ready. awaiting clients...")
except baseadmin.Error as e:
  reason = str(e)
  logging.error("baseAdmin could not be initialized: {0}".format(reason))
