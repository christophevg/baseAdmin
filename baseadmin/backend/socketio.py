import logging
logger = logging.getLogger(__name__)

from functools import wraps

from flask import request

from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect

from baseadmin.backend.web import server

from baseadmin.backend.repositories import registration, clients, groups

sid2name = {}

def current_client():
  return clients[sid2name[request.sid]]

socketio = SocketIO(server)

def emit_next(client):
  try:
    message = client.queue.get()
    if "schedule" in message and message["schedule"]:
      cmd = "schedule"
      payload = message
    else:
      cmd = message["cmd"]
      payload = {
        "args" : message["args"] if "args" in message else {},
      }
    logger.info("sending {0} to {1} with {2}".format(cmd, client.name, payload))
    socketio.emit(cmd, payload, room=client.name, callback=ack(client, cmd))
  except Exception as e:
    logger.exception(e)
    logger.error("couldn't emit next message, removing it from queue...")
    logger.error("message was: {0}".format(message))
    client.queue.pop()

def ack(client, cmd):
  def handler(feedback=None):
    with client.lock:
      if feedback:
        logger.info("ack: {0} : {1}  {2} => {3}".format(client.name, cmd, client.state, feedback["state"]))
        client.state = feedback["state"]
        client.queue.pop()
        d = dict(client)
        d["cmd"] = cmd
        socketio.emit("ack", d, room="browser" )
      else:
        logger.error("got no feedback from client, command no handled? {0}".format(cmd) )
        socketio.emit("error", "got no feedback from client, command no handled? {0}".format(cmd), room="browser")
        client.queue.pop()
      if not client.queue.empty: emit_next(client)
  return handler

# token-based authentication

from baseadmin.backend.repositories import tokens

def secured(f):
  @wraps(f)
  def wrapper(*args, **kwargs):
    try:
      name     = request.headers["client"]
      token    = request.headers["token"]
      expected = tokens.get(name)
      assert token == expected
      return f(*args, **kwargs)
    except Exception as e:
      logger.exception(e)
    except AssertionError:
      logger.warn( "invalid token: {0} expected: {1}) for {2}".format(token, expected, name))
      disconnect()
  return wrapper

# events

state_providers = {}

def register_state_provider(name, provider):
  global state_providers
  state_providers[name] = provider

@socketio.on('connect')
def on_connect():
  logger.info("connect: {0} ({1})".format(request.headers["client"], request.sid))
  name = request.headers["client"]
  token = request.headers["token"]
  if tokens.get(name) != token:
    logger.warn("invalid token {0} for {1} (expected {2})".format(token, name, tokens.get(name)))
    return False
  join_room(name)
  if name == "browser":
    state = {
      "clients"       : [ dict(client) for client in clients ],
      "registrations" : registration.get(),
      "groups"        : dict(groups)
    }
    for name, provider in state_providers.items(): state[name] = provider()
    emit( "state", state, room="browser" )
  else:
    client = clients[name]
    with client.lock:
      client.sid = request.sid
      sid2name[client.sid] = client.name
      emit("connected", client.name, room="browser")
      if not client.queue.empty: emit_next(client)

@socketio.on('disconnect')
def on_disconnect():
  logger.info("disconnect: {0} ({1})".format(request.headers["client"], request.sid))
  leave_room(request.headers["client"])
  name = request.headers["client"]
  if name != "browser":
    client = clients[name]
    if client.sid == request.sid:
      del sid2name[client.sid]
      client.sid = None
      emit("disconnected", client.name, room="browser")

@socketio.on("failure")
def on_failure(feedback):
  client = current_client()
  with client.lock:
    logger.warn("failure: {0} : {1} => {2}".format(client.name, client.state, feedback["state"]))
    client.state = feedback["state"]
    socketio.emit("failure", dict(client), room="browser" )

# commands

@socketio.on("queue")
@secured
def on_queue(message):
  queue(message["client"], message["payload"])

def queue(name, payload):
  def q(client, payload):
    with client.lock:
      logger.info("queue: {0} : {1}".format(client.name, payload))
      client.queue.append(payload)
      logger.info("queue length = {0}".format(str(len(client.queue))))
      if len(client.queue) == 1: emit_next(client)
  if name == "all":
    for client in clients:
      q(client, payload)
  elif name in groups:
    for member in groups[name]:
      client = clients[member]
      q(client, payload)
  else:
      q(clients[name], payload)


def command(cmd):
  def decorator(f):
    @wraps(f)
    @socketio.on(cmd)
    @secured
    def wrapper(data):
      try:
        f(data);
      except Exception as e:
        logger.exception("failed to perform {0}".format(cmd))
        return { "success" : False, "message" : str(e) }
      return { "success" : True }
    return wrapper
  return decorator
