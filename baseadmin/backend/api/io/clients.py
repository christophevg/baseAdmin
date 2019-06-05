import logging
logger = logging.getLogger(__name__)

from flask import request

from flask_socketio import emit

from baseadmin.backend.socketio     import socketio, secured, sid2name
from baseadmin.backend.repositories import registration, clients, groups

# commands

@socketio.on("accept")
@secured
def accept(message):
  logger.info("accept: {0}".format(message))
  try:
    registration.accept(message["client"], message["master"] if "master" in message else None)
  except Exception as e:
    return { "success" : False, "message" : str(e) }
  return { "success" : True }

@socketio.on("release")
@secured
def on_release(name):
  try:
    logger.info("cleaning up {0}".format(name))
    registration.delete(name)
    clients.delete(name)
    logger.info("releasing {0}".format(name))
    emit("release", {}, room=name)
  except Exception as e:
    return { "success" : False, "message" : str(e) }
  return { "success" : True }

@socketio.on("ping2")
@secured
def on_ping(data):
  name = data["client"]
  logger.info("ping {0}".format(name))
  if name in groups:
    for member in groups[name]:
      emit("ping2", data, room=member)
  else:
    emit("ping2", data, room=name)

@socketio.on("join")
@secured
def join(message):
  logger.info("join: {0}".format(message))
  try:
    groups[message["group"]].add(message["client"])
  except Exception as e:
    return { "success" : False, "message" : str(e) }
  return { "success" : True }

@socketio.on("leave")
@secured
def join(message):
  logger.info("leave: {0}".format(message))
  try:
    groups[message["group"]].remove(message["client"])
  except Exception as e:
    return { "success" : False, "message" : str(e) }
  return { "success" : True }

# events

@socketio.on("location")
@secured
def on_location(location):
  client = clients[sid2name[request.sid]]
  if client.location != location:
    logger.info("updating location for {0}: {1} -> {2}".format(
      client.name, client.location, location)
    )
    client.location = location
    socketio.emit("location", dict(client), room="browser" )

@socketio.on("performed")
@secured
def on_performed(feedback):
  client = clients[sid2name[request.sid]]
  with client.lock:
    client.state = feedback["state"]
    logger.info("performed: {0} : ")
    status = dict(client)
    status.update({ "performed" : feedback["performed"]})
    socketio.emit("performed", status, room="browser" )

@socketio.on("pong2")
@secured
def on_pong(data):
  name = sid2name[request.sid]
  logger.info("pong {0}".format(name))
  socketio.emit("pong2", data, room="browser")
