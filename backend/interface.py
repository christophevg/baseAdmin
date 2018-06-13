import os
from os import listdir
from os.path import isfile, join
import logging
import git

from flask  import render_template, send_from_directory
from flask  import request
from jinja2 import TemplateNotFound

from backend.web      import server
from backend.store    import store
from backend.security import authenticate

from backend import APP_NAME, APP_AUTHOR, APP_DESCRIPTION

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
      template + ".html",
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

@server.route("/static/main.js")
def send_main_js():
  repo = git.Repo(search_parent_directories=True)
  sha  = repo.head.object.hexsha
  info = {
    "git" : repo.git.rev_parse(sha, short=4)
  }
  return render_template(
    "main.js",
    info=info
  )

@server.route("/app/<path:filename>")
def send_app_static(filename):
  return send_from_directory("app", filename)

@server.route("/")
def render_home():
  return render("main", without_sections=True)

def list_services():
  path = os.path.join(os.path.dirname(__file__), "app")
  services = [os.path.splitext(f)[0] for f in listdir(path) if isfile(join(path, f))]
  return services

@server.route("/<path:section>")
@authenticate(["admin"])
def render_section(section):
  return render("main", services=list_services())
