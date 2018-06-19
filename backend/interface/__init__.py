import os

from flask  import render_template
from flask  import request
from jinja2 import TemplateNotFound

from backend import BACKEND_MODE, CLOUD, MASTER
from backend import APP_NAME, APP_AUTHOR, APP_DESCRIPTION

from backend.store import store

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

if MASTER: import backend.interface.master
if CLOUD:  import backend.interface.cloud
