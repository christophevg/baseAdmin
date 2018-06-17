import os
import logging

import backend.web
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

from backend.web import server

DEBUG = os.environ.get("BACKEND_DEBUG")
DEBUG = not DEBUG or DEBUG in [ "Yes", "yes", "Y", "y", "True", "true"]

PORT = os.environ.get("BACKEND_PORT")
if not PORT:
  port = 5000

server.run(debug=DEBUG, host="0.0.0.0", port=PORT)
