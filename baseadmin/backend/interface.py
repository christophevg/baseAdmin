import os
from os import listdir
from os.path import isfile, join

import logging

from flask  import render_template, send_from_directory
from flask  import request, redirect, abort
from jinja2 import TemplateNotFound

from baseadmin                      import config, __version__
from baseadmin.storage              import db
from baseadmin.backend.web          import server
from baseadmin.backend.security     import authenticated
from baseadmin.backend.repositories import users


def render(template="main.html"):
  user = None
  if request.authorization:
    user = users.get(request.authorization.username)
  try:
    return render_template(
      template,
      app=config.app,
      user=user,
      provision="true" if users.count() < 1 else "false"
    )
  except TemplateNotFound:
    abort(404)
  
@server.route("/")
def render_landing():
  logging.info("landing...")
  if request.authorization: return redirect("/dashboard", 302)
  return render()

@server.route("/static/js/main.js")
def send_main_js():
  return render("main.js")

# catch-all to always render the main page, which will handle the URL
@server.route("/<path:section>")
@authenticated("users")
def render_section(section):
  return render()
