import logging
logger = logging.getLogger()

from functools import wraps

from flask import request

from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect

from baseadmin.backend.web import server

from baseadmin.backend.repositories import registration, clients

sid2name = {}

socketio = SocketIO(server)

def emit_next(client):
  try:
    message = client.queue.get()
    if message["schedule"]:
      cmd = "schedule"
      payload = message
    else:
      cmd = message["cmd"]
      payload = {
        "args" : message["args"],
      }
    logger.info("sending {0} to {1} with {2}".format(cmd, client.name, payload))
    socketio.emit(cmd, payload, room=client.name, callback=ack(client))
  except Exception as e:
    logger.exception(e)
    logger.error("couldn't emit next message, removing it from queue...")
    logger.error("message was: {0}".format(message))
    client.queue.pop()

def ack(client):
  def handler(feedback):
    with client.lock:
      logger.info("ack: {0} : {1} => {2}".format(client.name, client.state, feedback["state"]))
      client.state = feedback["state"]
      client.queue.pop()
      socketio.emit("ack", dict(client), room="browser" )
      if not client.queue.empty: emit_next(client)
  return handler

# token-based authentication

from baseadmin.backend.repositories import tokens

def secured(f):
  @wraps(f)
  def wrapper(*args, **kwargs):
    try:
      name      = request.headers["client"]
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

# common

@socketio.on('connect')
def connect():
  logger.info("connect: {0} ({1})".format(request.headers["client"], request.sid))
  name = request.headers["client"]
  token = request.headers["token"]
  if tokens.get(name) != token:
    logger.warn("invalid token {0} for {1} (expected {2})".format(token, name, tokens.get(name)))
    return False
  join_room(name)
  if name == "browser":
    emit(
      "state",
      {
        "clients"       : [ dict(client) for client in clients ],
        "registrations" : registration.get()
      },
      room="browser")
  else:
    client = clients[name]
    with client.lock:
      client.sid = request.sid
      sid2name[client.sid] = client.name
      emit("connected", client.name, room="browser")
      if not client.queue.empty: emit_next(client)

@socketio.on('disconnect')
def disconnect():
  logger.info("disconnect: {0} ({1})".format(request.headers["client"], request.sid))
  leave_room(request.headers["client"])
  name = request.headers["client"]
  if name != "browser":
    client = clients[name]
    if client.sid == request.sid:
      del sid2name[client.sid]
      client.sid = None
      emit("disconnected", client.name, room="browser")

# browser

@socketio.on("queue")
@secured
def queue(message):
  client = clients[message["client"]]
  with client.lock:
    logger.info("queue: {0} : {1}".format(client.name, message["payload"]))
    client.queue.append(message["payload"])
    if len(client.queue) == 1: emit_next(client)
    return True

# client

@socketio.on("performed")
@secured
def performed(feedback):
  client = clients[sid2name[request.sid]]
  with client.lock:
    client.state = feedback["state"]
    logger.info("performed: {0} : ")
    status = dict(client)
    status.update({ "performed" : feedback["performed"]})
    socketio.emit("performed", status, room="browser" )
