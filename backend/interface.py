import os

from flask import render_template
from flask import request
from jinja2 import TemplateNotFound

from backend import app, authenticate, mongo

def render(template, without_sections=False):
  user = None
  if request.authorization:
    user = mongo.db.users.find_one({ "_id": request.authorization.username })
  app  = mongo.db.app.find_one({})
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

@app.route("/")
def render_home():
  return render("home", without_sections=True)

@app.route("/<string:section>")
@authenticate(["admin"])
def render_section(section):
  return render(section)
