from baseadmin.client.endpoint import Runner

try:
  endpoint = Runner()
  endpoint.connect()
except KeyboardInterrupt:
  pass

