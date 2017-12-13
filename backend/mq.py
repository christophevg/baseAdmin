import os

from urllib.parse import urlparse

CLOUDMQTT_URL = os.environ.get("CLOUDMQTT_URL")
if not CLOUDMQTT_URL:
  CLOUDMQTT_URL = "ws://localhost:9001"

MQ_URI = CLOUDMQTT_URL

p = urlparse(MQ_URI)
MQ_SSL      = p.scheme == "wss" or p.port == 19044
MQ_HOSTNAME = p.hostname
MQ_PORT     = 39044 if p.port == 19044 else p.port
MQ_USERNAME = p.username
MQ_PASSWORD = p.password
