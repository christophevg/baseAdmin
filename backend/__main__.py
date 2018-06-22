import os
import logging

from backend.web import server

DEBUG = os.environ.get("BACKEND_DEBUG")
DEBUG = not DEBUG or DEBUG in [ "Yes", "yes", "Y", "y", "True", "true"]

PORT = os.environ.get("BACKEND_PORT")
if not PORT:
  port = 5000

SSL = os.environ.get("SSL") in ["Yes", "yes", "Y", "y", "True", "true"]
if SSL:
  CERT = os.environ.get("SSL_CERT") or "etc/cert.pem"
  KEY  = os.environ.get("SSL_KEY")  or "etc/key.pem"
  context = (CERT, KEY)
  server.run(host='0.0.0.0', port=PORT, ssl_context=context, threaded=True, debug=True)
else:
  server.run(debug=DEBUG, host="0.0.0.0", port=PORT)
