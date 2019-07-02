import os

import logging
logger = logging.getLogger(__name__)

from flask  import render_template, send_from_directory
from flask  import request, redirect, abort
from jinja2 import TemplateNotFound

from baseadmin                      import config, __version__
from baseadmin.storage              import db
from baseadmin.backend.web          import server
from baseadmin.backend.security     import authenticated
from baseadmin.backend.repositories import users

components = {}

def render(template="main.html"):
  user = None
  if request.authorization:
    user = users.get(request.authorization.username)
  try:
    return render_template(
      template,
      app=config.app,
      user=user,
      provision="true" if users.count() < 1 else "false",
      components=components if users.count() > 0 else []
    )
  except TemplateNotFound:
    abort(404)
  
@server.route("/")
def render_landing():
  logging.info("landing...")
  if request.authorization: return redirect("/dashboard", 302)
  return render()

def register_component(filename, path):
  logger.info("registered component {0} from {1}".format(filename, path))
  components[filename] = path

@server.route("/app/<path:filename>")
@authenticated("users")
def send_app_static(filename):
  return send_from_directory(os.path.join(components[filename]), filename)

@server.route("/static/js/store.js")
# @authenticated("users")
def send_main_js():
  return render("store.js")


# catch-all to always render the main page, which will handle the URL

@server.route("/<path:section>")
@authenticated("users")
def render_section(section):
  return render()
