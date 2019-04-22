from baseadmin.client.endpoint import Node

try:
  Node().connect()
except KeyboardInterrupt:
  pass
