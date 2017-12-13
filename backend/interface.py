import os

from flask import render_template, send_from_directory
from flask import request
from jinja2 import TemplateNotFound

from backend.web import server
from backend.data import store

def render(template, without_sections=False):
  user = None
  if request.authorization:
    user = store.db.users.find_one({ "_id": request.authorization.username })
  app  = store.db.app.find_one({})
  try:
    return render_template(
      template + ".html",
      app=app,
      user=user,
      without_sections=without_sections
    )
  except TemplateNotFound:
    return render_template(
      "404.html",
      app=app,
      user=user,
      without_sections=True
    )

@server.route("/app/<path:filename>")
def send_app_static(filename):
  return send_from_directory("app/static", filename)


import backend.app.interface
