from backend import server, authenticate
from backend.interface import render

@server.route("/")
def render_home():
  return render("home", without_sections=True)

@server.route("/<string:section>")
@authenticate(["admin"])
def render_section(section):
  return render(section)
