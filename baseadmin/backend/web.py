import os
import logging

logger = logging.getLogger(__name__)

import traceback

from flask import Flask
import jinja2

reason = None

def server(environ, start_response):
  global reason
  data = "baseadmin could not be initialized: {0}\n".format(reason)
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

  import baseadmin.backend.interface
  import baseadmin.backend.api.rest
  import baseadmin.backend.api.io

  logger.info("baseadmin backend web server is ready. awaiting clients...")
except Exception as e:
  reason = str(e)
  logger.exception("baseadmin could not be initialized: {0}".format(reason))
