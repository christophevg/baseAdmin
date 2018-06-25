import os
from os.path import isfile, join
import git

from flask  import render_template

from backend.web      import server
from backend.security import authenticate

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
