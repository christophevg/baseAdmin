import os
import logging

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

  import baseadmin.backend.api
  # import baseadmin.backend.interface

  logging.info("baseadmin backend web server is ready. awaiting clients...")
except baseadmin.Error as e:
  reason = str(e)
  logging.error("baseadmin could not be initialized: {0}".format(reason))
