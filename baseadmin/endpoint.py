import logging

logger = logging.getLogger(__name__)

import sys
import requests
import json
import uuid
import bcrypt
import time
from functools import wraps
import dateutil.parser
import datetime
import signal

import warnings
warnings.simplefilter("ignore")

import engineio as eio
import socketio as sio

import warnings
warnings.simplefilter("ignore")

from baseadmin                             import config
from baseadmin.storage                     import db
from baseadmin.backend.repositories.client import Client

publish_location = False

def generate_location():
  return "https://{0}:8001".format(config.client.ip)

# override EngineIoClient to allow for unverified SSL connections

class MyEngineIoClient(eio.Client):
  def _send_request(self, method, url, headers=None, body=None):
    if self.http is None:
      self.http = requests.Session()
    try:
      return self.http.request(method, url, headers=headers, data=body, verify=False)
    except requests.exceptions.ConnectionError:
      pass

class MySocketIoClient(sio.Client):
  def _engineio_client_class(self):
    return MyEngineIoClient

socketio = MySocketIoClient()

me = Client(config.client.name, db.state)

# queue-base sending

def send(event, info):
  me.queue.append({ "event": event, "info": info})
  if len(me.queue) == 1: emit_next()

def emit_next():
  if not me.connected: return
  try:
    message = me.queue.get()
    logging.info("sending {0}".format(message))
    socketio.emit(message["event"], message["info"], callback=ack)
  except Exception as e:
    logger.exception(e)
    logger.error("couldn't emit next message, removing it from queue...")
    logger.error("message was: {0}".format(message))
    me.queue.pop()

def ack(feedback=None):
  with me.lock:
    message = me.queue.get()
    logger.info("ack {0} / {1}".format(message, feedback) )
    me.queue.pop()
    if not me.queue.empty: emit_next()

# event handlers

@socketio.on("connect")
def on_connect():
  logger.info("connected")
  me.sid = socketio.eio.sid
  if publish_location:
    location = generate_location()
    logger.info("sending location: {0}".format(location))
    socketio.emit("location", location)
  socketio.emit("refresh", feedback()) # send refresh of state on connect
  if not me.queue.empty: emit_next()

@socketio.on("error")
def on_error(msg):
  logger.info(msg)

@socketio.on("disconnect")
def on_disconnect():
  logger.info("disconnected")
  me.sid = None
  socketio.disconnect()

@socketio.on("release")
def on_release(_):
  logger.info("release")
  socketio.disconnect()

@socketio.on("ping2")
def on_ping(request):
  logger.info("ping")
  socketio.emit("pong2", request)

@socketio.on("schedule")
def on_schedule(cmd):
  logger.info("received scheduled cmd: {0}".format(cmd))
  try:
    cmd["schedule"] = dateutil.parser.parse(cmd["schedule"]).timestamp()
    now = datetime.datetime.utcnow().timestamp()
    logger.info("now={0} / schedule={1} / eta={2}".format(now, cmd["schedule"], cmd["schedule"]-now))
    me.schedule.add(cmd)
  except Exception as e:
    feedback(failure=str(e))
  return feedback()

commands = {}

def perform_scheduled_tasks():
  while True:
    try:
      scheduled = me.schedule.get()
      while scheduled and scheduled["schedule"] <= datetime.datetime.utcnow().timestamp():
        logger.info("performing scheduled cmd: {0}".format(scheduled) )
        commands[scheduled["cmd"]](scheduled["args"])
        me.schedule.pop()
        send("performed", feedback(performed=scheduled))
        scheduled = me.schedule.get()
        socketio.sleep(0.05)
    except Exception as e:
      pass
    socketio.sleep(0.05)

socketio.start_background_task(perform_scheduled_tasks)

# command decorator

def feedback(*args, **kwargs):
  # logger.info("state: {0} + {1}".format(me.state, me.schedule.items))
  feedback = {
    "name": me.name,
    "state" : {
      "current" : me.state,
      "futures" : me.schedule.items
    }
  }
  feedback.update(kwargs)
  feedback.update({ "feedback" : args })
  return feedback

def command(cmd):
  def decorator(f):
    commands[cmd] = f
    @wraps(f)
    @socketio.on(cmd)
    def wrapper(data):
      try:
        return feedback(f(data["args"]))
      except Exception as e:
        logger.exception("execution of command failed: {0}".format(str(e)))
      return feedback()
    return wrapper
  return decorator

# register/connection management

def send_registration_request(url, token):
  try:
    response = requests.post(
      url,
      auth=(config.client.name, config.client.secret),
      json={ "token" : token },
      verify=False
    )
  except requests.ConnectionError:
    logger.warn("could not connect to {0}".format(url))
    return ( None, None )
  except Exception as e:
    logger.exception("failed to connect")
    return ( None, None )

  # failure
  if response.status_code != requests.codes.ok:
    logger.warn("failed to register: {0}".format(str(response)))
    return ( None, None )

  feedback = response.json()
  logging.debug("feedback: {0}".format(feedback))

  # pending
  if not feedback:
    logger.info("registration is pending")
    return ( None, None )

  # rejected
  if feedback["state"] == "rejected":
    logger.warn("registration was rejected")
    return ( "rejected", None )

  # accepted
  logger.info("registration was accepted: {0}".format(feedback["master"]))

  return ("accepted", feedback["master"] )

def register(master, token):
  url = master + "/api/register"
  logger.info("registering at {0} with token {1}".format(url, token))
  while True:
    (outcome, other_master) = send_registration_request(url, token)
    if outcome == "rejected": return None
    if outcome == "accepted":
      # go to redirected master
      if other_master: return register(other_master, token)
      # store this master and provided token as our current master/token pair
      db.config.update_one( {"_id": "master"},{ "$set" : { "value": master } }, upsert=True )
      db.config.update_one( {"_id": "token"}, { "$set" : { "value": token } },  upsert=True )
      return master
    logger.debug("retrying in {0}".format(str(config.master.registration_interval)))
    config.master.registration_interval.sleep()

def connect(master, token):
  if socketio.eio.state == "connected":
    logger.warn("trying to connect while socketio already connected ?")
    return True

  logger.info("connecting to {0} using {1}".format(master, token))
  for retry in range(config.master.connection_retries):
    try:
      socketio.connect(
        master,
        headers={
          "client": config.client.name,
          "token" : token
        })
      return True
    except sio.exceptions.ConnectionError as e:
      logger.warn("can't connect to master ({0})".format(master))
      if retry+1 < config.master.connection_retries:
        logger.debug("retrying connection in {0}".format(str(config.master.connection_interval)))
        config.master.connection_interval.sleep()
  logger.error("failed to connect after retries")
  return False

def run():
  logger.info("starting event loop...")
  
  master = None
  token  = str(uuid.uuid4())

  # load the current connection parameters
  try:
    master = db.config.find_one({"_id": "master"})["value"]
    token  = db.config.find_one({"_id": "token" })["value"]  
  except:
    # no connection info could be loaded, start at root with fresh token
    logging.info("no connecting info, starting registration")
    master = register(config.master.root, token)

  while master:
    while connect(master, token):
      socketio.wait()
      logger.debug("============= stopped waiting ==============")
    # can't connect, re-register
    logger.debug("clearing registration")
    db.config.delete_one({"_id": "master"})
    db.config.delete_one({"_id": "token"})
    master = register(config.master.root, token)

  logger.fatal("registration was rejected, can't continue.")
  return False

# temp solution for easier termination of endpoint
def my_teardown_handler(signal, frame):
  socketio.disconnect()
  sys.exit(1)
signal.signal(signal.SIGINT, my_teardown_handler)
