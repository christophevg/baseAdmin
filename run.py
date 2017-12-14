import backend.config

from backend.web import server

backend.mq.track_clients()
backend.mq.connect("backend")
server.run(debug=True, host="0.0.0.0")
