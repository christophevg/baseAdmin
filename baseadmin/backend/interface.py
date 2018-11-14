import os
from os import listdir
from os.path import isfile, join

import logging

from flask  import render_template, send_from_directory
from flask  import request
from jinja2 import TemplateNotFound

from baseadmin.backend import __version__
from baseadmin.backend import config

from baseadmin.backend.web      import server
from baseadmin.backend.security import authenticate
from baseadmin.backend.store    import store

def render(template, **kwargs):
  user = None
  if request.authorization:
    user = store.users.find_one({ "_id": request.authorization.username })
  try:
    return render_template(
      template + ".html",
      app=config,
      user=user,
      **kwargs
    )
  except TemplateNotFound:
    return render_template(
      "404.html",
      app=config,
      user=user,
      without_sections=True
    )

@server.route("/")
@authenticate(["admin"])
def render_home():
  return render("main", services=list_services())

@server.route("/<path:section>")
@authenticate(["admin"])
def render_section(section):
  return render("main", services=list_services())

@server.route("/static/js/main.js")
@authenticate(["admin"])
def send_main_js():
  info = {
    "version" : __version__
  }
  return render_template("main.js", info=info)

@server.route("/static/js/router.js")
@authenticate(["admin"])
def send_router_js():
  return render_template("router.js")

@server.route("/app/<path:filename>")
@authenticate(["admin"])
def send_app_static(filename):
  return send_from_directory(os.path.join(config["root"], "media", "js"), filename)

def list_services():
  try:
    path = os.path.join(config["root"], "media", "js")
    services = [os.path.splitext(f)[0] for f in listdir(path) if isfile(join(path, f))]
    return sorted(services)
  except OSError:
    return []
