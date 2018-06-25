import os

from flask  import send_from_directory

from backend.web       import server
from backend.security  import authenticate

from backend.interface import render

# Heroku/Cloud doesn't expose git repository

@server.route("/static/main.js")
def send_main_js():
  return send_from_directory(os.path.join("templates", "cloud"), "main.js")

