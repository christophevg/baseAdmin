import os

from flask  import send_from_directory

from backend.web       import server
from backend.security  import authenticate

from backend.interface import render

@server.route("/static/main.js")
def send_main_js():
  return send_from_directory(os.path.join("templates", "cloud"), "main.js")

@server.route("/")
@authenticate(["admin"])
def render_home():
  return render("main", services=[])

@server.route("/<path:section>")
@authenticate(["admin"])
def render_section(section):
  return render("main", services=[])
