if __name__ == '__main__':
  import os
  from backend.web import server
  
  DEBUG = os.environ.get("BACKEND_DEBUG")
  DEBUG = not DEBUG or DEBUG in [ "Yes", "yes", "Y", "y", "True", "true"]

  PORT = os.environ.get("BACKEND_PORT")
  if not PORT:
    port = 5000
  
  server.run(debug=DEBUG, host="0.0.0.0", port=PORT)
