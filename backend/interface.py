import os
from os import listdir
from os.path import isfile, join

from flask  import render_template, send_from_directory
from flask  import request
from jinja2 import TemplateNotFound

from backend import __version__
from backend import BACKEND_MODE, CLOUD, MASTER
from backend import APP_NAME, APP_AUTHOR, APP_DESCRIPTION

from backend.web      import server
from backend.security import authenticate
from backend.store    import store

def render(template, **kwargs):
  user = None
  if request.authorization:
    user = store.users.find_one({ "_id": request.authorization.username })
  app = {
    "name"        : APP_NAME,
    "author"      : APP_AUTHOR,
    "description" : APP_DESCRIPTION
  }
  try:
    return render_template(
      os.path.join(BACKEND_MODE, template + ".html"),
      app=app,
      user=user,
      **kwargs
    )
  except TemplateNotFound:
    return render_template(
      "404.html",
      app=app,
      user=user,
      without_sections=True
    )

@server.route("/app/<path:filename>")
@authenticate(["admin"])
def send_app_static(filename):
  return send_from_directory(os.path.join("app", BACKEND_MODE), filename)

def list_services():
  path = os.path.join(os.path.dirname(__file__), "app", BACKEND_MODE)
  services = [os.path.splitext(f)[0] for f in listdir(path) if isfile(join(path, f))]
  return sorted(services)

@server.route("/")
@authenticate(["admin"])
def render_home():
  return render("main", services=list_services())

@server.route("/<path:section>")
@authenticate(["admin"])
def render_section(section):
  return render("main", services=list_services())

@server.route("/static/main.js")
@authenticate(["admin"])
def send_main_js():
  info = {
    "version" : __version__
  }
  return render_template(
    os.path.join(BACKEND_MODE, "main.js"),
    info=info
  )

@server.route("/static/router.js")
@authenticate(["admin"])
def send_router_js():
  return render_template(
    os.path.join("master", "router.js")
  )
