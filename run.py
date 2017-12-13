from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), "env.local")
load_dotenv(dotenv_path)

from backend.web import server

server.run(debug=True, host="0.0.0.0")
