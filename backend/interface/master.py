import os
from os import listdir
from os.path import isfile, join
import logging
import git

from flask  import render_template, send_from_directory
from flask  import request
from jinja2 import TemplateNotFound

from backend.web      import server
from backend.security import authenticate

from backend.interface import render

@server.route("/static/main.js")
@authenticate(["admin"])
def send_main_js():
  repo = git.Repo(search_parent_directories=True)
  sha  = repo.head.object.hexsha
  info = {
    "git" : repo.git.rev_parse(sha, short=4)
  }
  return render_template(
    os.path.join("master", "main.js"),
    info=info
  )

@server.route("/app/<path:filename>")
@authenticate(["admin"])
def send_app_static(filename):
  return send_from_directory("app", filename)

def list_services():
  path = os.path.join(os.path.dirname(__file__), "..", "app")
  services = [os.path.splitext(f)[0] for f in listdir(path) if isfile(join(path, f))]
  return services

@server.route("/")
@authenticate(["admin"])
def render_home():
  return render("main", services=list_services())

@server.route("/<path:section>")
@authenticate(["admin"])
def render_section(section):
  return render("main", services=list_services())
