import logging

logger = logging.getLogger(__name__)

import requests
import json
import uuid
import bcrypt
import time
from functools import wraps
import dateutil.parser
import datetime

import warnings
warnings.simplefilter("ignore")

import engineio as eio
import socketio as sio

import warnings
warnings.simplefilter("ignore")

from baseadmin                             import config
from baseadmin.storage                     import db
from baseadmin.backend.repositories.client import Client


def register(registration={}, master=config.master.root):
  url = master + "/api/register"
  logger.info("registering at {0}".format(url))
  while True:
    try:
      logger.debug("submitting registration: {0}".format(str(registration)))
      response = requests.post(
        url,
        data=json.dumps(registration),
        headers={"content-type": "application/json"},
        auth=(config.client.name, config.client.secret),
        verify=False
      )
      if response.status_code != requests.codes.ok:
        logger.warn("failed to register: {0}".format(str(response)))
      else:
        request = response.json()
        if request:
          logger.info(request)
          if request["state"] == "accepted":
            logger.info("registration was accepted: {0}/{1}".format(
              request["master"], request["token"]
            ))
            if request["master"] is None:
              db.config.update_one(
                {"_id": "master"},
                { "$set" : { "value": master } },
                upsert=True
              )
              db.config.update_one(
                {"_id": "token"},
                { "$set" : { "value": request["token"] } },
                upsert=True
              )
              return True
            else:
              return register(registration, request["master"])
          elif request["state"] == "rejected":
            logger.warn("registration was rejected")
            return False
        logger.info("registration is pending")
    except requests.ConnectionError:
      logger.warn("could not connect to {0}".format(url))
    except Exception as e:
      logger.exception("failed to connect")
    logger.debug("retrying in {0}".format(str(config.master.interval)))
    config.master.interval.sleep()

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

def ack():
  with me.lock:
    message = me.queue.get()
    logger.info("ack {0}".format(message) )
    me.queue.pop()
    if not me.queue.empty: emit_next()

@socketio.on("connect")
def on_connect():
  logger.info("connected")
  me.sid = socketio.eio.sid
  if not me.queue.empty: emit_next()

@socketio.on("disconnect")
def on_disconnect():
  logger.info("disconnected")
  me.sid = None

commands = {}

def feedback(*args, **kwargs):
  logger.info("state: {0} + {1}".format(me.state, me.schedule.items))
  feedback = {
    "state" : {
      "current" : me.state,
      "futures" : me.schedule.items
    }
  }
  feedback.update(kwargs)
  return feedback
  
def command(cmd):
  def decorator(f):
    commands[cmd] = f
    @wraps(f)
    @socketio.on(cmd)
    def wrapper(data):
      return feedback(f(data["args"]))
    return wrapper
  return decorator

@socketio.on("schedule")
def on_schedule(cmd):
  logger.info("received scheduled cmd: {0}".format(cmd))
  cmd["schedule"] = dateutil.parser.parse(cmd["schedule"]).timestamp()
  now = datetime.datetime.utcnow().timestamp()
  logger.info("now={0} / schedule={1} / eta={2}".format(now, cmd["schedule"], cmd["schedule"]-now))
  me.schedule.add(cmd)
  return feedback()

def perform_scheduled_tasks():
  while True:
    scheduled = me.schedule.get()
    while scheduled and scheduled["schedule"] <= datetime.datetime.utcnow().timestamp():
      logger.info("performing scheduled cmd: {0}".format(scheduled) )
      commands[scheduled["cmd"]](scheduled["args"])
      me.schedule.pop()
      send("performed", feedback(performed=scheduled))
      scheduled = me.schedule.get()
    socketio.sleep(0.05)

socketio.start_background_task(perform_scheduled_tasks)

def connect():
  if socketio.eio.state == "connected": return
  master = db.config.find_one({"_id": "master"})["value"]
  token   = db.config.find_one({"_id": "token"})["value"]
  logger.info("connecting to {0} using {1}".format(master, token))
  while True:
    try:
      socketio.connect(
        master,
        headers={
          "client": config.client.name,
          "token" : token
        })
      return True
    except sio.exceptions.ConnectionError as e:
      logger.warn("couldn't connect")
      logger.exception(e)
      logger.info("retrying in 3 seconds...")
      time.sleep(3)
  return False

def run():
  logging.info("starting...")
  while connect():
    try:
      while socketio.eio.state == "connected":
        socketio.wait()
        logger.info("stopped waiting")
    except KeyboardInterrupt:
      socketio.disconnect()
      return
    except Exception as e:
      socketio.disconnect()
      logger.exception(e)
