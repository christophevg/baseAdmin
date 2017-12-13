from flask import Flask
import jinja2

server = Flask(__name__)

my_loader = jinja2.ChoiceLoader([
  jinja2.FileSystemLoader("backend/app/templates/"),
  server.jinja_loader,
])
server.jinja_loader = my_loader
